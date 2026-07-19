"""IT之家爬虫 — RSS Feed。"""
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper, ScraperError

logger = logging.getLogger(__name__)

RSS_URL = "https://www.ithome.com/rss/"


class IthomeScraper(BaseScraper):
    source_id = "ithome"
    category = "tech"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        resp = self._get(RSS_URL)
        resp.encoding = "utf-8"
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as e:
            raise ScraperError(f"ithome RSS parse error: {e}")

        items = root.findall(".//item")
        logger.info("ithome RSS returned %d items", len(items))
        articles = []
        for item in items:
            title = _text(item, "title")
            link = _text(item, "link")
            pub_date = _text(item, "pubDate")
            desc = _text(item, "description")
            author = _text(item, "author") or "IT之家"

            if not title or not link:
                continue

            summary = ""
            content_raw = desc
            if desc:
                soup = BeautifulSoup(desc, "lxml")
                summary = soup.get_text(separator=" ", strip=True)[:300]
                content_raw = desc

            articles.append(self._build_article(
                title=title, url=link, author=author,
                summary=summary, content_raw=content_raw,
                published_at=pub_date,
            ))
        return articles


def _text(el, tag):
    child = el.find(tag)
    return child.text.strip() if child is not None and child.text else ""
