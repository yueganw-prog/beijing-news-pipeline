"""
Tests for Beijing News Pipeline API.

Usage:
  pip install pytest pytest-asyncio httpx
  cd api && pytest test_main.py -v
"""

from contextlib import asynccontextmanager
from datetime import datetime, date, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# -------------------------------------------------------
# Prevent the real lifespan from trying to connect to a DB.
# We patch asyncpg BEFORE importing main, then override
# the lifespan with a no-op that keeps our fake pool.
# -------------------------------------------------------

# We'll import main once, but neutralize its lifespan:
import main

# Save the real app for reference; we replace its lifespan below.
from main import app as _app


# -------------------------------------------------------
# FakeRecord — behaves like an asyncpg Record row.
# dict(r) works because we implement keys() + __getitem__.
# -------------------------------------------------------

class FakeRecord:
    """Simulates an asyncpg Record row: attribute access + dict() support."""

    def __init__(self, **kwargs):
        self._data = dict(kwargs)
        self.__dict__.update(kwargs)

    def keys(self):
        return self._data.keys()

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return f"<FakeRecord {self._data}>"


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

_ARTICLE_DEFAULTS = {
    "id": 1,
    "source": "36kr",
    "category": "tech",
    "title": "测试标题",
    "url": "https://example.com/article/1",
    "author": "作者名",
    "summary": "摘要内容",
    "content_raw": "<p>原始正文</p>",
    "content_clean": "清洗后正文",
    "published_at": datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc),
    "fetched_at": datetime(2026, 7, 19, 13, 0, tzinfo=timezone.utc),
    "minio_bucket": "articles",
    "minio_key": "tech/36kr/1.json",
    "language": "zh",
    "metadata": '{"views": 100}',
    "created_at": datetime(2026, 7, 19, 13, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 7, 19, 13, 0, tzinfo=timezone.utc),
}


def _row(**overrides):
    """Build a FakeRecord that looks like an articles table row."""
    data = dict(_ARTICLE_DEFAULTS)
    data.update(overrides)
    return FakeRecord(**data)


def _mock_pool():
    """Return a (pool, conn) tuple — fresh mock with an acquired connection."""
    conn = AsyncMock()
    pool = MagicMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    pool.close = AsyncMock()
    return pool, conn


# -------------------------------------------------------
# Kill the real lifespan before any test runs.
# The app's startup tries to connect to a real database;
# we swap in a no-op lifespan that keeps our fake pool.
# -------------------------------------------------------

def _install_noop_lifespan():
    """Replace the app's lifespan with a no-op that preserves main.pool."""
    @asynccontextmanager
    async def _noop(_app_obj):
        # Don't touch main.pool — tests set it themselves
        yield

    _app.router.lifespan_context = _noop


_install_noop_lifespan()


# -------------------------------------------------------
# Fixtures
# -------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_env():
    """Reset API_KEY before every test so auth tests don't leak state."""
    main.API_KEY = ""
    yield


@pytest.fixture
def client():
    """Provide an httpx AsyncClient wired to the FastAPI app."""
    return AsyncClient(transport=ASGITransport(app=_app), base_url="http://test")


# -------------------------------------------------------
# 1. Health
# -------------------------------------------------------

class TestHealth:
    async def test_ok(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetchval = AsyncMock(return_value=1)
        main.pool = pool

        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok", "database": "connected"}

    async def test_db_down(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetchval = AsyncMock(side_effect=Exception("Connection refused"))
        main.pool = pool

        r = await client.get("/health")
        assert r.status_code == 503
        body = r.json()
        assert body["detail"]["status"] == "error"
        assert "Connection refused" in body["detail"]["database"]


# -------------------------------------------------------
# 2. List articles
# -------------------------------------------------------

class TestListArticles:
    async def test_default_pagination(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[_row(id=i) for i in range(1, 4)])
        main.pool = pool

        r = await client.get("/articles")
        assert r.status_code == 200
        assert len(r.json()) == 3

    async def test_filter_by_source(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[_row(source="huxiu")])
        main.pool = pool

        r = await client.get("/articles?source=huxiu")
        assert r.status_code == 200
        assert r.json()[0]["source"] == "huxiu"

    async def test_filter_by_category(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[])
        main.pool = pool

        r = await client.get("/articles?category=finance")
        assert r.status_code == 200
        assert r.json() == []

    async def test_combined_filter(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[])
        main.pool = pool

        await client.get("/articles?source=36kr&category=tech&limit=10&offset=0")
        # Parameterized query — values are in the params tuple, not the SQL string
        sql: str = conn.fetch.call_args[0][0]
        params = conn.fetch.call_args[0][1:]
        assert "source" in sql and "category" in sql  # column names in SQL
        assert "36kr" in params and "tech" in params  # values in params


# -------------------------------------------------------
# 3. Single article
# -------------------------------------------------------

class TestGetArticle:
    async def test_found(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetchrow = AsyncMock(return_value=_row(id=42, title="独家新闻"))
        main.pool = pool

        r = await client.get("/articles/42")
        assert r.status_code == 200
        assert r.json()["title"] == "独家新闻"

    async def test_not_found(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetchrow = AsyncMock(return_value=None)
        main.pool = pool

        r = await client.get("/articles/99999")
        assert r.status_code == 404


# -------------------------------------------------------
# 4. Full-text search
# -------------------------------------------------------

class TestSearch:
    async def test_search_with_results(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[_row(title="人工智能爆发")])
        main.pool = pool

        r = await client.get("/articles/search?q=人工智能")
        assert r.status_code == 200
        assert len(r.json()) == 1

    async def test_missing_query(self, client: AsyncClient):
        pool, conn = _mock_pool()
        main.pool = pool

        r = await client.get("/articles/search")
        assert r.status_code == 422

    async def test_empty_query(self, client: AsyncClient):
        pool, conn = _mock_pool()
        main.pool = pool

        r = await client.get("/articles/search?q=")
        assert r.status_code == 422


# -------------------------------------------------------
# 5. Stats
# -------------------------------------------------------

class TestStats:
    async def test_by_source(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[
            FakeRecord(source="36kr", category="tech", cnt=100,
                       last_fetched=datetime(2026, 7, 19, tzinfo=timezone.utc))
        ])
        main.pool = pool

        r = await client.get("/stats/by-source")
        assert r.status_code == 200
        assert r.json()[0]["cnt"] == 100


# -------------------------------------------------------
# 6. DQ Results
# -------------------------------------------------------

class TestDQResults:
    async def test_list_all(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[
            FakeRecord(id=1, dag_run_id="run_001", source="36kr",
                       category="tech", total_rows=50, score=95.5,
                       checked_at=datetime(2026, 7, 19, tzinfo=timezone.utc))
        ])
        main.pool = pool

        r = await client.get("/dq-results")
        assert r.status_code == 200
        assert r.json()[0]["score"] == 95.5

    async def test_filter_by_dag_run(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[])
        main.pool = pool

        await client.get("/dq-results?dag_run_id=run_002")
        sql: str = conn.fetch.call_args[0][0]
        params = conn.fetch.call_args[0][1:]
        assert "dag_run_id" in sql
        assert "run_002" in params


# -------------------------------------------------------
# 7. Pipeline Runs
# -------------------------------------------------------

class TestPipelineRuns:
    async def test_list_all(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[
            FakeRecord(id=1, dag_id="beijing_news_pipeline",
                       dag_run_id="run_x", run_date=date(2026, 7, 19),
                       status="success", total_articles=200, dq_avg_score=88.0,
                       started_at=datetime(2026, 7, 19, 8, 0, tzinfo=timezone.utc),
                       finished_at=datetime(2026, 7, 19, 8, 15, tzinfo=timezone.utc))
        ])
        main.pool = pool

        r = await client.get("/pipeline-runs")
        assert r.status_code == 200
        data = r.json()
        assert data[0]["status"] == "success"
        assert data[0]["total_articles"] == 200

    async def test_filter_by_status(self, client: AsyncClient):
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[])
        main.pool = pool

        await client.get("/pipeline-runs?status=failed")
        sql: str = conn.fetch.call_args[0][0]
        params = conn.fetch.call_args[0][1:]
        assert "status" in sql
        assert "failed" in params


# -------------------------------------------------------
# 8. Validation edge cases
# -------------------------------------------------------

class TestAuth:
    async def test_health_bypasses_auth(self, client: AsyncClient):
        """Health endpoint works without API key even when auth is enabled."""
        pool, conn = _mock_pool()
        conn.fetchval = AsyncMock(return_value=1)
        main.pool = pool
        main.API_KEY = "secret123"  # enable auth

        r = await client.get("/health")
        assert r.status_code == 200

    async def test_articles_requires_key(self, client: AsyncClient):
        """Protected endpoint returns 401 without X-API-Key header."""
        pool, conn = _mock_pool()
        main.pool = pool
        main.API_KEY = "secret123"

        r = await client.get("/articles")
        assert r.status_code == 401
        assert "API key" in r.json()["detail"]

    async def test_articles_with_good_key(self, client: AsyncClient):
        """Protected endpoint accepts valid X-API-Key header."""
        pool, conn = _mock_pool()
        conn.fetch = AsyncMock(return_value=[_row()])
        main.pool = pool
        main.API_KEY = "secret123"

        r = await client.get("/articles", headers={"X-API-Key": "secret123"})
        assert r.status_code == 200

    async def test_articles_with_bad_key(self, client: AsyncClient):
        """Protected endpoint rejects wrong X-API-Key header."""
        pool, conn = _mock_pool()
        main.pool = pool
        main.API_KEY = "secret123"

        r = await client.get("/articles", headers={"X-API-Key": "wrong-key"})
        assert r.status_code == 401


class TestValidation:
    async def test_articles_limit_too_high(self, client: AsyncClient):
        pool, conn = _mock_pool()
        main.pool = pool

        r = await client.get("/articles?limit=1000")
        assert r.status_code == 422

    async def test_articles_limit_zero(self, client: AsyncClient):
        pool, conn = _mock_pool()
        main.pool = pool

        r = await client.get("/articles?limit=0")
        assert r.status_code == 422

    async def test_search_limit_too_high(self, client: AsyncClient):
        pool, conn = _mock_pool()
        main.pool = pool

        r = await client.get("/articles/search?q=test&limit=999")
        assert r.status_code == 422
