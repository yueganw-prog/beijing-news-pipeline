"""管道运行脚本 - 执行完整 DAG 逻辑：依赖检查 -> 采集 -> DQ -> 归档 -> 记录。
无需 Airflow，直接调用爬虫和数据库。"""
import asyncio, asyncpg, io, json, logging, os, sys
from datetime import datetime



sys.path.insert(0, r"C:\Users\admin\Desktop\beijing-news-pipeline\dags")
from scrapers import fetch_source

DSN = "postgresql://postgres:postgres@localhost:5432/airflow"
BUCKET = "news-archive"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline")

SOURCES = [
    ("36kr", "tech"), ("huxiu", "tech"), ("ithome", "tech"),
    ("sina_finance", "finance"), ("yicai", "finance"), ("eeo", "finance"),
    ("bjnews", "local"), ("bjdaily", "local"), ("bjbusiness", "local"),
]

# ── 0. 依赖检查 ────────────────────────────────────
def check_deps():
    """检查 MinIO 和 PostgreSQL 连通性（同步）。"""
    results = {"postgres": False, "minio": False}
    # MinIO
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:9000/minio/health/live",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            results["minio"] = resp.status == 200
    except Exception as e:
        logger.error("MinIO check failed: %s", e)
    # PG via asyncpg in a subprocess-friendly way
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect(("localhost", 5432))
        s.close()
        results["postgres"] = True
    except Exception as e:
        logger.error("PG check failed: %s", e)
    return results

# ── 1. 采集 ────────────────────────────────────────
def fetch_all():
    """采集全部源，返回 {source_id: [articles]}。"""
    all_arts = {}
    for sid, cat in SOURCES:
        try:
            arts = fetch_source(sid, cat)
            logger.info("[%s] %d articles", sid, len(arts))
            all_arts[sid] = arts
        except Exception as e:
            logger.error("[%s] FAIL: %s", sid, e)
            all_arts[sid] = []
    return all_arts

# ── 2. DQ 检查 ─────────────────────────────────────
def dq_check(all_arts):
    """计算 DQ 分数，返回结果字典。"""
    articles = []
    for arts in all_arts.values():
        articles.extend(arts)
    total = len(articles)
    if total == 0:
        return {"score": 0, "total_rows": 0}
    nt = sum(1 for a in articles if not a.get("title"))
    nu = sum(1 for a in articles if not a.get("url"))
    nc = sum(1 for a in articles if not a.get("content_raw"))
    urls = [a.get("url","") for a in articles if a.get("url")]
    dup = len(urls) - len(set(urls)) if urls else 0
    cls = [len(a.get("content_raw","")) for a in articles]
    avg_l = sum(cls)/len(cls) if cls else 0
    min_l = min(cls) if cls else 0
    deductions = (nt/total*20)+(nu/total*20)+(nc/total*30)+(dup/total*15)
    if min_l < 300:
        deductions += min(15,(300-min_l)/300*15)
    score = round(max(0,100-deductions),2)
    return {
        "total_rows": total, "score": score,
        "null_title": nt, "null_url": nu, "null_content": nc,
        "dup_url_count": dup, "min_content_len": min_l,
        "avg_content_len": round(avg_l,2),
    }

# ── 3. MinIO 归档 ──────────────────────────────────
def archive_minio(all_arts):
    """上传文章 JSON 到 MinIO。"""
    from minio import Minio
    mc = Minio(
        "localhost:9000",
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        secure=False,
        region="us-east-1",
    )
    try:
        found = mc.bucket_exists(BUCKET)
    except Exception as e:
        logger.warning("MinIO connect error, trying with default region: %s", e)
        mc = Minio(
            "localhost:9000",
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
            secure=False,
        )
        found = mc.bucket_exists(BUCKET)
    if not found:
        mc.make_bucket(BUCKET)
        logger.info("MinIO bucket '%s' created", BUCKET)
    today = datetime.now().strftime("%Y/%m/%d")
    n = 0
    for sid, arts in all_arts.items():
        for art in arts:
            key = f"{today}/{sid}/{art.get('title','untitled')[:80]}.json"
            data = json.dumps(art, ensure_ascii=False).encode("utf-8")
            mc.put_object(BUCKET, key, io.BytesIO(data), len(data))
            n += 1
    logger.info("Archived %d articles to MinIO bucket '%s'", n, BUCKET)
    return {"bucket": BUCKET, "archived_count": n}

# ── 4. 写入运行记录 ─────────────────────────────────
async def write_run_record(dq, archive, all_arts):
    """写入 pipeline_runs 表。"""
    dag_run_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(
            """INSERT INTO dq_results
            (dag_run_id, task_id, source, category, total_rows,
             null_title, null_url, null_content, dup_url_count,
             min_content_len, avg_content_len, score, details)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13::jsonb)""",
            dag_run_id, "dq_check", "__merged__", "__all__",
            dq["total_rows"], dq["null_title"], dq["null_url"],
            dq["null_content"], dq["dup_url_count"],
            dq["min_content_len"], dq["avg_content_len"],
            dq["score"], json.dumps(dq),
        )
        status = "success" if dq["score"] > 50 else "partial"
        await conn.execute(
            """INSERT INTO pipeline_runs
            (dag_id, dag_run_id, run_date, status, started_at, finished_at,
             total_sources, success_sources, total_articles,
             dq_avg_score, minio_archive)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11::jsonb)""",
            "beijing_news_pipeline", dag_run_id,
            datetime.now().date(), status,
            datetime.now(), datetime.now(),
            len(SOURCES), len([1 for v in all_arts.values() if v]),
            dq["total_rows"], dq["score"],
            json.dumps(archive),
        )
        logger.info("Run record: %s (%s) score=%.1f", dag_run_id, status, dq["score"])
    finally:
        await conn.close()

# ── main ───────────────────────────────────────────
async def main():
    logger.info("=== Pipeline Start ===")
    deps = check_deps()
    logger.info("Deps: PG=%s MinIO=%s", deps["postgres"], deps["minio"])
    if not deps["postgres"]:
        logger.error("PostgreSQL unreachable, aborting")
        return
    all_arts = fetch_all()
    dq = dq_check(all_arts)
    logger.info("DQ: score=%.1f rows=%d null_title=%d dup=%d",
        dq["score"], dq["total_rows"], dq["null_title"], dq["dup_url_count"])
    archive = {}
    try:
        archive = archive_minio(all_arts)
    except Exception as e:
        logger.warning("MinIO archive skipped: %s", e)
        archive = {"bucket": BUCKET, "archived_count": 0, "error": str(e)}
    await write_run_record(dq, archive, all_arts)
    logger.info("=== Pipeline Complete ===")

asyncio.run(main())
