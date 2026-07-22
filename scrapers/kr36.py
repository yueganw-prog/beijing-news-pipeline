"""36氪爬虫 — RSS Feed。"""
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper, ScraperError

logger = logging.getLogger(__name__)

RSS_URL = "https://36kr.com/feed"
TZ_RE = re.compile(r"[+-]\d{4}$")


def _parse_date(raw: str) -> str:
    if not raw:
        return datetime.now().isoformat()
    try:
        raw = TZ_RE.sub("", raw).strip()
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    except ValueError:
        return raw


class Kr36Scraper(BaseScraper):
    source_id = "36kr"
    category = "tech"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        resp = self._get(RSS_URL)
        resp.encoding = "utf-8"
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as e:
            raise ScraperError(f"36kr RSS parse error: {e}")

        items = root.findall(".//item")
        logger.info("36kr RSS returned %d items", len(items))
        articles = []
        for item in items:
            ns = {"dc": "http://purl.org/dc/elements/1.1/"}
            title = _text(item, "title")
            link = _text(item, "link")
            pub_date = _text(item, "pubDate")
            desc = _text(item, "description")
            creator = _text(item, "dc:creator", ns)
            if not title or not link:
                continue

            # Extract author from description HTML
            author = creator or "36氪"
            if desc:
                m = re.search(r"<p>文[｜｜](.+?)</p>", desc)
                if m:
                    author = m.group(1).strip()
                    author = re.sub(r"<[^>]+>", "", author)

            # Strip HTML from description for summary, keep raw for content
            summary = ""
            content_raw = desc
            if desc:
                soup = BeautifulSoup(desc, "lxml")
                summary = soup.get_text(separator=" ", strip=True)[:300]
                content_raw = desc  # Keep full HTML

            articles.append(self._build_article(
                title=title, url=link, author=author,
                summary=summary, content_raw=content_raw,
                published_at=_parse_date(pub_date),
            ))
        return articles


def _text(el, tag, ns=None):
    child = el.find(tag, ns) if ns else el.find(tag)
    return child.text.strip() if child is not None and child.text else ""
