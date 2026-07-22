"""经济观察报爬虫 — 栏目列表 + 桌面端文章正文。"""
import logging
import re
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)

COLUMN_URLS = [
    "https://www.eeo.com.cn/jg/tuijian/jingjiguanchabao/",
    "https://www.eeo.com.cn/",
]
MAX_ARTICLES = 15
ARTICLE_RE = re.compile(r".*/(\d{4})/(\d{4})/(\d+)\.shtml")
AUTHOR_RE = re.compile(r'\u6587[/\uff0f](\S+)')


def _url_date(entry):
    mmdd = entry["mmdd"]
    return f"{entry['year']}-{mmdd[:2]}-{mmdd[2:]}T00:00:00"


class EeoScraper(BaseScraper):
    source_id = "eeo"
    category = "finance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self):
        links_seen = set()
        entries = []
        for col_url in COLUMN_URLS:
            try:
                resp = self._get(col_url)
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = BeautifulSoup(resp.text, "lxml")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    m = ARTICLE_RE.match(href)
                    if not m:
                        continue
                    text = a.get_text(strip=True)
                    if len(text) < 5:
                        continue
                    if href in links_seen:
                        continue
                    links_seen.add(href)
                    entries.append(dict(url=href, title_list=text, year=m.group(1), mmdd=m.group(2), nid=m.group(3)))
                    if len(entries) >= MAX_ARTICLES:
                        break
                logger.info("eeo from %s: %d entries total", col_url.split("/")[2], len(entries))
                if len(entries) >= MAX_ARTICLES:
                    break
            except Exception:
                logger.warning("eeo listing failed for %s", col_url)
        logger.info("eeo total list: %d entries (max %d)", len(entries), MAX_ARTICLES)
        articles = []
        for entry in entries:
            try:
                art = self._fetch_article(entry)
                articles.append(art)
            except Exception:
                logger.warning("eeo article fail: %s", entry["url"])
                articles.append(self._build_article(title=entry["title_list"], url=entry["url"], author="\u7ecf\u6d4e\u89c2\u5bdf\u62a5", published_at=_url_date(entry)))
        return articles

    def _fetch_article(self, entry):
        resp = self._get(entry["url"])
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        title_tag = soup.find("h1")
        title = ""
        if title_tag:
            title = title_tag.get_text(strip=True)
            title = title.replace("-\u7ecf\u6d4e\u89c2\u5bdf\u7f51", "").strip()
        if not title:
            title = entry["title_list"]
        cd = soup.find("div", class_="xd-bottom")
        content = ""
        author = "\u7ecf\u6d4e\u89c2\u5bdf\u62a5"
        if cd:
            content = cd.get_text(separator="\n", strip=True)
            m = AUTHOR_RE.search(content)
            if m:
                author = m.group(1)
        return self._build_article(title=title, url=entry["url"], author=author, content_raw=content[:5000], published_at=_url_date(entry))
