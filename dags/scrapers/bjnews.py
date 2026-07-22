"""新京报爬虫 — 主页 HTML 解析。"""
import logging
import re
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)

PAGE_URL = "https://www.bjnews.com.cn/"
MAX_ARTICLES = 20
URL_RE = re.compile(r"/detail/(\d+)")


class BjnewsScraper(BaseScraper):
    source_id = "bjnews"
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
            m = URL_RE.search(href)
            if not m:
                continue
            text = a.get_text(strip=True)
            if len(text) < 5:
                continue
            if href in links_seen:
                continue
            links_seen.add(href)
            if not href.startswith("http"):
                href = "https://www.bjnews.com.cn" + href
            # Try fetching article page for description
            summary = ""
            content_raw = ""
            try:
                ar = self._get(href, timeout=10)
                ar.encoding = ar.apparent_encoding or "utf-8"
                soup_ar = BeautifulSoup(ar.text, "lxml")
                # Meta description
                dm = soup_ar.find("meta", attrs={"name": "description"})
                if dm and dm.get("content"):
                    summary = dm["content"].strip()
                # Also look for article body text
                for tag in soup_ar.find_all(["div", "article"]):
                    cls = " ".join(tag.get("class", []))
                    txt = tag.get_text(strip=True)
                    if "article" in cls.lower() and len(txt) > 100:
                        content_raw = txt[:3000]
                        break
            except Exception:
                pass

            articles.append(self._build_article(
                title=text, url=href, author="新京报",
                summary=summary, content_raw=content_raw,
            ))
            if len(articles) >= MAX_ARTICLES:
                break
        logger.info("bjnews found %d articles", len(articles))
        return articles
