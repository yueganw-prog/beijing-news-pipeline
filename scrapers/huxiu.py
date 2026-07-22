"""虎嗅爬虫 — RSS Feed。"""
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper, ScraperError

logger = logging.getLogger(__name__)

RSS_URL = "https://rss.huxiu.com/"


def _parse_date(raw: str) -> str:
    if not raw:
        return datetime.now().isoformat()
    try:
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(raw.strip(), fmt)
                return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            except ValueError:
                continue
    except Exception:
        pass
    return raw


class HuxiuScraper(BaseScraper):
    source_id = "huxiu"
    category = "tech"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        resp = self._get(RSS_URL, timeout=30)
        resp.encoding = "utf-8"
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as e:
            raise ScraperError(f"Huxiu RSS parse error: {e}")

        items = root.findall(".//item")
        logger.info("Huxiu RSS returned %d items", len(items))
        articles = []
        for item in items:
            title = _text(item, "title")
            link = _text(item, "link")
            pub_date = _text(item, "pubDate")
            desc = _text(item, "description")
            author_tag = item.find("author")
            author = author_tag.text.strip() if author_tag is not None and author_tag.text else ""
            if not author:
                author = "虎嗅"
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
                published_at=_parse_date(pub_date),
            ))
        return articles


def _text(el, tag):
    child = el.find(tag)
    return child.text.strip() if child is not None and child.text else ""
