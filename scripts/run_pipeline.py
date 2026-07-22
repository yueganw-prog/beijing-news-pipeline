"""新闻管道完整运行脚本 — 采集 → 入库 → DQ → 归档 → 记录。

一次执行完成全部环节，无需 Airflow：
  1. 爬取 9 个新闻源
  2. 写入 articles 表（URL 去重）
  3. DQ 质量检查
  4. 归档到 MinIO
  5. 写入 pipeline_runs 运行记录

用法：
  python scripts/run_pipeline.py
"""

import asyncio, asyncpg, io, json, logging, os, re, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scrapers import fetch_source

DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/airflow")
# asyncpg needs a clean URL without +asyncpg prefix
DSN = DSN.replace("+asyncpg", "")
BUCKET = "news-archive"
ENABLE_MINIO = os.getenv("ENABLE_MINIO", "false").lower() in ("1", "true", "yes")
SOURCES = [
    ("36kr", "tech"), ("huxiu", "tech"), ("ithome", "tech"),
    ("sina_finance", "finance"), ("yicai", "finance"), ("eeo", "finance"),
    ("bjnews", "local"), ("bjdaily", "local"), ("bjbusiness", "local"),
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline")

_html_re = re.compile(r"<[^>]+>")
_ws_re = re.compile(r"\s+")


def _clean(text):
    """去除 HTML 标签，规范化空白。"""
    if not text:
        return ""
    return _ws_re.sub(" ", _html_re.sub("", text)).strip()


# ============================================================
# 1. 采集 + 入库
# ============================================================

async def fetch_and_insert():
    """爬取全部源并写入 articles 表（URL 去重）。"""
    conn = await asyncpg.connect(DSN)
    all_arts = {}
    total = 0

    for sid, cat in SOURCES:
        try:
            articles = await asyncio.to_thread(fetch_source, sid, cat)
        except Exception as e:
            logger.error("[%s] 爬取失败: %s", sid, e)
            all_arts[sid] = []
            continue

        inserted = 0
        for art in articles:
            try:
                await conn.execute(
                    """INSERT INTO articles
                    (source, category, title, url, author, summary,
                     content_raw, content_clean, published_at, fetched_at)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                    ON CONFLICT (url) DO NOTHING""",
                    art["source"], art["category"],
                    art["title"], art["url"],
                    art.get("author", ""),
                    art.get("summary", ""),
                    art.get("content_raw", ""),
                    _clean(art.get("content_raw", "")),
                    art.get("published_at"),
                    datetime.now(),
                )
                inserted += 1
            except Exception as e:
                logger.debug("[%s] 插入失败: %s", sid, e)

        all_arts[sid] = articles
        total += inserted
        logger.info("[%s] %d 篇采集, %d 篇新入库", sid, len(articles), inserted)

    await conn.close()
    logger.info("入库完成，共 %d 篇新文章", total)
    return all_arts, total


# ============================================================
# 2. DQ 检查
# ============================================================

def dq_check(all_arts: dict) -> dict:
    """计算数据质量分数。"""
    articles = []
    for arts in all_arts.values():
        articles.extend(arts)

    total = len(articles)
    if total == 0:
        return {"score": 0, "total_rows": 0}

    nt = sum(1 for a in articles if not a.get("title"))
    nu = sum(1 for a in articles if not a.get("url"))
    nc = sum(1 for a in articles if not a.get("content_raw"))
    urls = [a.get("url", "") for a in articles if a.get("url")]
    dup = len(urls) - len(set(urls)) if urls else 0
    cls = [len(a.get("content_raw", "")) for a in articles]
    avg_l = sum(cls) / len(cls) if cls else 0
    min_l = min(cls) if cls else 0

    deductions = (nt / total * 20) + (nu / total * 20) + (nc / total * 30) + (dup / total * 15)
    if min_l < 300:
        deductions += min(15, (300 - min_l) / 300 * 15)

    score = round(max(0, 100 - deductions), 2)
    return {
        "total_rows": total, "score": score,
        "null_title": nt, "null_url": nu, "null_content": nc,
        "dup_url_count": dup, "min_content_len": min_l,
        "avg_content_len": round(avg_l, 2),
    }


# ============================================================
# 3. MinIO 归档
# ============================================================

def archive_minio(all_arts: dict) -> dict:
    """Upload article JSON to MinIO (optional — skipped if ENABLE_MINIO is false)."""
    if not ENABLE_MINIO:
        logger.info("MinIO disabled (ENABLE_MINIO=%s), skipping archive.", os.getenv("ENABLE_MINIO", "false"))
        return {"bucket": BUCKET, "archived_count": 0, "disabled": True}

    from minio import Minio

    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    mc = Minio(
        endpoint.replace("http://", "").replace("https://", ""),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        secure=False,
    )
    if not mc.bucket_exists(BUCKET):
        mc.make_bucket(BUCKET)
        logger.info("MinIO bucket '%s' 已创建", BUCKET)

    today = datetime.now().strftime("%Y/%m/%d")
    n = 0
    for sid, arts in all_arts.items():
        for art in arts:
            key = f"{today}/{sid}/{art.get('title', 'untitled')[:80]}.json"
            data = json.dumps(art, ensure_ascii=False).encode("utf-8")
            mc.put_object(BUCKET, key, io.BytesIO(data), len(data))
            n += 1

    logger.info("归档 %d 篇到 MinIO", n)
    return {"bucket": BUCKET, "archived_count": n}


# ============================================================
# 4. 写入运行记录
# ============================================================

async def _write_run_record(dq: dict, archive: dict, new_count: int):
    """写入 dq_results 和 pipeline_runs 表。"""
    dag_run_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    conn = await asyncpg.connect(DSN)

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
        new_count, dq["score"],
        json.dumps(archive),
    )

    logger.info("运行记录: %s (%s) score=%.1f", dag_run_id, status, dq["score"])
    await conn.close()


# ============================================================
# main
# ============================================================

def main():
    logger.info("=== 管道开始 ===")

    # 1. 采集 + 入库
    all_arts, new_count = asyncio.run(fetch_and_insert())

    # 2. DQ
    dq = dq_check(all_arts)
    logger.info("DQ: score=%.1f rows=%d null_title=%d dup=%d",
                dq["score"], dq["total_rows"], dq["null_title"], dq["dup_url_count"])

    # 3. 归档
    archive = {}
    try:
        archive = archive_minio(all_arts)
    except Exception as e:
        logger.warning("MinIO 归档跳过: %s", e)
        archive = {"bucket": BUCKET, "archived_count": 0, "error": str(e)}

    # 4. 运行记录
    asyncio.run(_write_run_record(dq, archive, new_count))

    logger.info("=== 管道完成 ===")


if __name__ == "__main__":
    main()
