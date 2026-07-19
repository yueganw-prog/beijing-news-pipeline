"""种子数据脚本 - 运行全部爬虫并将结果写入 PostgreSQL。"""
import asyncio, asyncpg, sys, os
import re
from datetime import datetime
from dateutil.parser import parse as parse_date

sys.path.insert(0, r"C:\Users\admin\Desktop\beijing-news-pipeline\dags")
from scrapers import fetch_source

DSN = "postgresql://postgres:postgres@localhost:5432/airflow"

SOURCES = [
    ("36kr", "tech"),
    ("huxiu", "tech"),
    ("ithome", "tech"),
    ("sina_finance", "finance"),
    ("yicai", "finance"),
    ("eeo", "finance"),
    ("bjnews", "local"),
    ("bjdaily", "local"),
    ("bjbusiness", "local"),
]

def _parse_published(raw):
    if not raw:
        return datetime.now()
    try:
        return datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        try:
            return parse_date(raw)
        except Exception:
            return datetime.now()

async def main():
    conn = await asyncpg.connect(DSN)
    total = 0
    for sid, cat in SOURCES:
        try:
            articles = fetch_source(sid, cat)
        except Exception as e:
            print(f"  [{sid}] FAIL: {e}")
            continue

        n = 0
        for art in articles:
            try:
                await conn.execute(
                    """INSERT INTO articles
                    (source, category, title, url, author, summary, content_raw, content_clean, published_at, fetched_at)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                    ON CONFLICT (url) DO NOTHING""",
                    art["source"], art["category"],
                    art["title"], art["url"],
                    art.get("author", ""),
                    art.get("summary", ""),
                    art.get("content_raw", ""),
                    _clean(art.get("content_raw", "")),
                    _parse_published(art.get("published_at")),
                    datetime.now(),
                )
                n += 1
            except Exception as e:
                print(f"    [{sid}] insert error: {e}")
        total += n
        print(f"  [{sid}] {len(articles)} fetched, {n} new")
    await conn.close()
    print(f"\nTotal new articles: {total}")

_html_re = re.compile(r'<[^>]+>')
_ws_re = re.compile(r'\s+')

def _clean(text):
    """Strip HTML, normalize whitespace."""
    if not text:
        return ""
    return _ws_re.sub(' ', _html_re.sub('', text)).strip()

asyncio.run(main())
