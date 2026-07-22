"""北京商报爬虫 — 主页 HTML 解析。"""
import logging
import re
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)

PAGE_URL = "https://www.bbtnews.com.cn/"
MAX_ARTICLES = 20
DATE_URL_RE = re.compile(r"/2026/\d{4}/\d+\.shtml")


class BjbusinessScraper(BaseScraper):
    source_id = "bjbusiness"
    category = "local"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        resp = self._get(PAGE_URL)
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        links_seen = set()
        articles = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not DATE_URL_RE.search(href):
                continue
            text = a.get_text(strip=True)
            if len(text) < 5:
                continue
            if href in links_seen:
                continue
            links_seen.add(href)
            if not href.startswith("http"):
                href = "http://www.bbtnews.com.cn" + href
            # Fetch article page for description and content
            summary = ""
            content_raw = ""
            try:
                ar = self._get(href, timeout=10)
                ar.encoding = ar.apparent_encoding or "utf-8"
                soup_ar = BeautifulSoup(ar.text, "lxml")
                dm = soup_ar.find("meta", attrs={"name": "description"})
                if dm and dm.get("content"):
                    summary = dm["content"].strip()
                # Look for article content divs
                for tag in soup_ar.find_all(["div"]):
                    cls = " ".join(tag.get("class", []))
                    txt = tag.get_text(strip=True)
                    if "article" in cls.lower() and len(txt) > 100:
                        content_raw = txt[:3000]
                        break
            except Exception:
                pass

            articles.append(self._build_article(
                title=text, url=href, author="北京商报",
                summary=summary, content_raw=content_raw,
            ))
            if len(articles) >= MAX_ARTICLES:
                break
        logger.info("bjbusiness found %d articles", len(articles))
        return articles
