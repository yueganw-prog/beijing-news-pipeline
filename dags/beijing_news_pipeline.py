"""Beijing News Aggregation Pipeline - Airflow DAG

Tech: 36kr / Huxiu / ithome
Finance: Sina Finance / Yicai / EEO
Local: Beijing News / Beijing Daily / Beijing Business
"""

import json
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task, dag
from airflow.models import Variable, Param
from airflow.utils.trigger_rule import TriggerRule
from scrapers import fetch_source

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

DEFAULT_SOURCES = {
    "tech": [
        {"id": "36kr",        "name": "36氪",        "base_url": "https://36kr.com"},
        {"id": "huxiu",       "name": "虎嗅",        "base_url": "https://www.huxiu.com"},
        {"id": "ithome",      "name": "IT之家",       "base_url": "https://www.ithome.com"},
    ],
    "finance": [
        {"id": "sina_finance", "name": "新浪财经",     "base_url": "https://finance.sina.com.cn"},
        {"id": "yicai",        "name": "第一财经",     "base_url": "https://www.yicai.com"},
        {"id": "eeo",          "name": "经济观察报",   "base_url": "https://www.eeo.com.cn"},
    ],
    "local": [
        {"id": "bjnews",       "name": "新京报",      "base_url": "https://www.bjnews.com.cn"},
        {"id": "bjdaily",      "name": "北京日报",    "base_url": "https://www.bjd.com.cn"},
        {"id": "bjbusiness",   "name": "北京商报",    "base_url": "https://www.bbtnews.com.cn"},
    ],
}


def _get_sources():
    try:
        return Variable.get("news_sources", deserialize_json=True)
    except Exception:
        return DEFAULT_SOURCES


@dag(
    dag_id="beijing_news_pipeline",
    description="Beijing news aggregation: tech/finance/local articles -> clean -> DQ -> archive",
    default_args=DEFAULT_ARGS,
    schedule="0 8,18 * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["beijing", "news", "aggregation"],
    params={
        "source_override": Param(
            default=None, type=["null", "object"],
            description="JSON override for news source list",
        ),
        "categories": Param(
            default=["tech", "finance", "local"], type="array",
            description="Category subset for this run",
        ),
    },
    max_active_runs=1,
)
def beijing_news_pipeline():
    """Beijing news aggregation pipeline DAG."""

    @task(task_id="check_dependencies")
    def check_deps(**context):
        """Check PostgreSQL / MinIO connectivity"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        results = {"postgres": False, "minio": False}
        try:
            hook = PostgresHook(postgres_conn_id="news_postgres")
            conn = hook.get_conn()
            conn.cursor().execute("SELECT 1")
            results["postgres"] = True
            conn.close()
        except Exception as e:
            logger.error("PG check failed: %s", e)
        try:
            import os
            from minio import Minio
            mc = Minio(os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
                secure=False,
            )
            mc.list_buckets()
            results["minio"] = True
        except Exception as e:
            logger.error("MinIO check failed: %s", e)
        context["ti"].xcom_push(key="dep_check", value=results)
        if not results["postgres"]:
            raise ConnectionError("PostgreSQL unreachable - pipeline cannot continue")
        if not results["minio"]:
            logger.warning("MinIO unreachable - archive tasks will be skipped but pipeline continues")
        return results

    @task
    def fetch_one(source: dict, category: str, **context):
        """Fetch a single source via scrapers module."""
        logger.info("Fetching [%s/%s] %s", category, source["id"], source["name"])
        try:
            articles = fetch_source(source["id"], category)
        except Exception as e:
            logger.error("Scraper [%s] failed: %s", source["id"], e)
            raise
        if not articles:
            logger.warning("Scraper [%s] returned 0 articles", source["id"])
        else:
            logger.info("Scraper [%s] returned %d articles", source["id"], len(articles))
        context["ti"].xcom_push(key="articles_%s" % source["id"], value=articles)
        return articles

    @task(task_id="dq_check", trigger_rule=TriggerRule.ALL_DONE)
    def quality_check(**context):
        """Merge results, DQ scoring, write to dq_results"""
        ti = context["ti"]
        all_articles = []
        for category, src_list in _get_sources().items():
            for src in src_list:
                try:
                    arts = ti.xcom_pull(task_ids="fetch_%s" % src["id"], key="articles_%s" % src["id"])
                    if arts:
                        all_articles.extend(arts)
                except Exception:
                    pass

        total = len(all_articles)
        nt = sum(1 for a in all_articles if not a.get("title"))
        nu = sum(1 for a in all_articles if not a.get("url"))
        nc = sum(1 for a in all_articles if not a.get("content_raw"))
        urls = [a.get("url", "") for a in all_articles if a.get("url")]
        dup = len(urls) - len(set(urls))
        cls = [len(a.get("content_raw", "")) for a in all_articles]
        avg_l = sum(cls) / len(cls) if cls else 0
        min_l = min(cls) if cls else 0

        deductions = 0 if total > 0 else 100
        if total > 0:
            deductions += (nt / total) * 20
            deductions += (nu / total) * 20
            deductions += (nc / total) * 30
            deductions += (dup / total) * 15
            if min_l < 300:
                deductions += min(15, (300 - min_l) / 300 * 15)
        score = round(max(0, 100 - deductions), 2)

        result = {
            "dag_run_id": context["dag_run"].run_id,
            "total_rows": total, "score": score,
            "null_title": nt, "null_url": nu, "null_content": nc,
            "dup_url_count": dup, "min_content_len": min_l,
            "avg_content_len": round(avg_l, 2),
        }

        from airflow.providers.postgres.hooks.postgres import PostgresHook
        hook = PostgresHook(postgres_conn_id="news_postgres")
        hook.run(
            "INSERT INTO dq_results "
            "(dag_run_id, task_id, source, category, total_rows, "
            "null_title, null_url, null_content, dup_url_count, "
            "min_content_len, avg_content_len, score, details) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)",
            parameters=(
                result["dag_run_id"], "dq_check", "__merged__", "__all__",
                result["total_rows"],
                result["null_title"], result["null_url"],
                result["null_content"], result["dup_url_count"],
                result["min_content_len"], result["avg_content_len"],
                result["score"], json.dumps(result),
            ),
        )
        ti.xcom_push(key="dq_result", value=result)
        return result

    @task(task_id="archive_minio", trigger_rule=TriggerRule.ALL_DONE)
    def archive(**context):
        """Archive articles to MinIO"""
        import io, os
        from minio import Minio
        ti = context["ti"]
        run_date = context["dag_run"].execution_date.strftime("%Y/%m/%d")
        bucket = "news-archive"
        mc = Minio(os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
            secure=False,
        )
        if not mc.bucket_exists(bucket):
            mc.make_bucket(bucket)
        n = 0
        for _, src_list in _get_sources().items():
            for src in src_list:
                arts = ti.xcom_pull(task_ids="fetch_%s" % src["id"], key="articles_%s" % src["id"])
                if not arts:
                    continue
                for art in arts:
                    key = "%s/%s/%s.json" % (run_date, src["id"], art.get("title", "untitled")[:80])
                    data = json.dumps(art, ensure_ascii=False).encode("utf-8")
                    mc.put_object(bucket, key, io.BytesIO(data), len(data))
                    n += 1
        result = {"bucket": bucket, "archived_count": n}
        ti.xcom_push(key="archive_result", value=result)
        return result

    @task(task_id="update_pipeline_run", trigger_rule=TriggerRule.ALL_DONE)
    def record_run(**context):
        """Write to pipeline_runs table"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        dag_run = context["dag_run"]
        ti = context["ti"]
        dq = ti.xcom_pull(task_ids="dq_check", key="dq_result") or {}
        archive_res = ti.xcom_pull(task_ids="archive_minio", key="archive_result") or {}
        total_src = sum(len(v) for v in _get_sources().values())
        hook = PostgresHook(postgres_conn_id="news_postgres")
        hook.run(
            "INSERT INTO pipeline_runs "
            "(dag_id, dag_run_id, run_date, status, started_at, "
            "total_sources, success_sources, total_articles, "
            "dq_avg_score, minio_archive) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)",
            parameters=(
                dag_run.dag_id, dag_run.run_id,
                dag_run.execution_date.date(),
                "success" if dq.get("score", 0) > 50 else "partial",
                dag_run.start_date or datetime.now(),
                total_src, total_src,
                dq.get("total_rows", 0), dq.get("score"),
                json.dumps(archive_res),
            ),
        )
        return {"dag_run_id": dag_run.run_id, "status": "recorded"}

    dep = check_deps()

    fetchers = []
    for category, src_list in _get_sources().items():
        for src in src_list:
            fetchers.append(
                fetch_one.override(task_id="fetch_%s" % src["id"])(source=src, category=category)
            )

    dep >> fetchers >> quality_check() >> archive() >> record_run()


register_dag = beijing_news_pipeline()
