"""Beijing Daily scraper - rolling news regex extraction + article page title."""
import logging
import re
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseScraper
from datetime import date

logger = logging.getLogger(__name__)

ROLL_URL = "https://news.bjd.com.cn/roll/"
MAX_ARTICLES = 20
ARTICLE_RE = re.compile(r"/(\d{4}/\d{2}/\d{2}/\d+\.shtml)")
URL_BASE = "https://news.bjd.com.cn"


class BjdailyScraper(BaseScraper):
    source_id = "bjdaily"
    category = "local"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        resp = self._get(ROLL_URL)
        resp.encoding = resp.apparent_encoding or "utf-8"
        seen = set()
        articles = []
        urls = ARTICLE_RE.findall(resp.text)
        logger.info("bjdaily found %d url patterns in roll page", len(urls))
        today = date.today().strftime("%Y/%m/%d")
        for path in urls:
            if today not in path:
                continue
            url = URL_BASE + "/" + path
            if url in seen:
                continue
            seen.add(url)
            title = path.split("/")[-1].replace(".shtml", "")
            author = "Beijing Daily"
            summary = ""
            soup = None
            try:
                ar = self._get(url, timeout=10)
                ar.encoding = ar.apparent_encoding or "utf-8"
                soup = BeautifulSoup(ar.text, "lxml")
                title_tag = soup.find("title")
                if title_tag:
                    t = title_tag.get_text(strip=True)
                    t = t.replace("_Beijing News", "").strip()
                    if t:
                        title = t
                desc_meta = soup.find("meta", attrs={"name": "description"})
                if desc_meta and desc_meta.get("content"):
                    summary = desc_meta["content"].strip()
                author_meta = soup.find("meta", attrs={"name": "author"})
                if author_meta and author_meta.get("content"):
                    author = author_meta["content"].strip()
            except Exception:
                logger.warning("bjdaily article fetch failed: %s", url)

            content_raw = ""
            if soup is not None:
                try:
                    for tag in soup.find_all(["div", "article"]):
                        cls = " ".join(tag.get("class", []))
                        txt = tag.get_text(strip=True)
                        if (
                            "article" in cls.lower() or "content" in cls.lower()
                        ) and len(txt) > 200:
                            content_raw = txt[:3000]
                            break
                except Exception:
                    pass

            articles.append(
                self._build_article(
                    title=title,
                    url=url,
                    author=author,
                    summary=summary,
                    content_raw=content_raw,
                )
            )
            if len(articles) >= MAX_ARTICLES:
                break
        logger.info("bjdaily returning %d articles", len(articles))
        return articles
