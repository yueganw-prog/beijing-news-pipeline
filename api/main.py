# Beijing News Pipeline - FastAPI query service

from contextlib import asynccontextmanager
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/airflow")
# asyncpg needs a clean URL without +asyncpg
DSN = DATABASE_URL.replace("+asyncpg", "")

pool: asyncpg.Pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(DSN, min_size=2, max_size=10)
    yield
    await pool.close()


app = FastAPI(title="Beijing News API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

# --- API Key auth (optional — disabled when API_KEY is unset) ---

API_KEY = os.getenv("API_KEY", "")


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if API_KEY and request.url.path != "/health":
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid API key. Provide X-API-Key header."},
            )
    return await call_next(request)

# --- Schemas ---

class ArticleOut(BaseModel):
    id: int
    source: str
    category: str
    title: str
    url: str
    author: str
    summary: str
    published_at: Optional[datetime] = None
    fetched_at: datetime

    content_clean: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DQResultOut(BaseModel):
    id: int
    dag_run_id: str
    source: str
    category: str
    total_rows: int
    score: Optional[float] = None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineRunOut(BaseModel):
    id: int
    dag_id: str
    dag_run_id: str
    run_date: date
    status: str
    total_articles: int
    dq_avg_score: Optional[float] = None
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Endpoints ---

@app.get("/health")
async def health():
    """Health check"""
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(503, detail={"status": "error", "database": str(e)})


@app.get("/articles", response_model=list[ArticleOut])
async def list_articles(
    source: Optional[str] = Query(None, description="News source id"),
    category: Optional[str] = Query(None, description="Category: tech/finance/local"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Query article list, supports filtering by source and category"""
    where = []
    params = []
    idx = 1
    if source:
        where.append(f"source = ${idx}")
        params.append(source)
        idx += 1
    if category:
        where.append(f"category = ${idx}")
        params.append(category)
        idx += 1
    where_sql = " AND ".join(where) if where else "TRUE"

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"SELECT * FROM articles WHERE {where_sql} ORDER BY fetched_at DESC LIMIT ${idx} OFFSET ${idx+1}",
            *params, limit, offset,
        )
    return [dict(r) for r in rows]


@app.get("/articles/search", response_model=list[ArticleOut])
async def search_articles(
    q: str = Query(..., min_length=1, description="Search keyword"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Full text search articles by title/summary/content"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT *, ts_rank(
                to_tsvector("simple", coalesce(title,'') || ' ' || coalesce(summary,'') || ' ' || coalesce(content_raw,'')),
                plainto_tsquery("simple", $1)
            ) AS rank
            FROM articles
            WHERE to_tsvector("simple", coalesce(title,'') || ' ' || coalesce(summary,'') || ' ' || coalesce(content_raw,''))
                  @@ plainto_tsquery("simple", $1)
            ORDER BY rank DESC, fetched_at DESC
            LIMIT $2 OFFSET $3""",
            q, limit, offset,
        )
    return [dict(r) for r in rows]


@app.get("/articles/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int):
    """Get single article detail"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM articles WHERE id = $1", article_id)
    if not row:
        raise HTTPException(404, "Article not found")
    return dict(row)


@app.get("/stats/by-source")
async def stats_by_source():
    """Stats by source"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT source, category, COUNT(*) as cnt, "
            "MAX(fetched_at) as last_fetched "
            "FROM articles GROUP BY source, category ORDER BY cnt DESC"
        )
    return [dict(r) for r in rows]


@app.get("/dq-results", response_model=list[DQResultOut])
async def list_dq_results(
    limit: int = Query(20, ge=1, le=200),
    dag_run_id: Optional[str] = None,
):
    """Recent DQ check results"""
    if dag_run_id:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM dq_results WHERE dag_run_id = $1 ORDER BY checked_at DESC LIMIT $2",
                dag_run_id, limit,
            )
    else:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM dq_results ORDER BY checked_at DESC LIMIT $1", limit
            )
    return [dict(r) for r in rows]


@app.get("/pipeline-runs", response_model=list[PipelineRunOut])
async def list_pipeline_runs(
    limit: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
):
    """Pipeline run records"""
    if status:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM pipeline_runs WHERE status = $1 ORDER BY run_date DESC LIMIT $2",
                status, limit,
            )
    else:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM pipeline_runs ORDER BY run_date DESC LIMIT $1", limit
            )
    return [dict(r) for r in rows]
