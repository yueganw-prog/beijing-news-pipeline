"""第一财经爬虫 — 新闻列表 API。"""
import logging
from typing import Dict, List

from .base import BaseScraper, ScraperError
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

API_URL = "https://www.yicai.com/api/ajax/getlistbycid"
API_PARAMS = {
    "cid": "48",
    "page": "1",
    "pagesize": "30",
}


class YicaiScraper(BaseScraper):
    """第一财经新闻爬虫。

    通过 JSON API 获取文章列表。文章正文在第一财经网站需
    付费授权才能查看，因此只使用 API 返回的摘要字段。
    """

    source_id = "yicai"
    category = "finance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        resp = self._get_json(API_URL, params=API_PARAMS)
        if not isinstance(resp, list):
            raise ScraperError(
                f"第一财经 API 返回格式异常: {type(resp)}"
            )
        logger.info("第一财经 API 返回 %d 篇文章", len(resp))

        articles = []
        for item in resp:
            title = item.get("NewsTitle", "")
            share_url = item.get("ShareUrl", "")
            news_id = item.get("NewsID")

            if not title:
                continue

            # URL: 优先 ShareUrl，否则用 NewsID 拼接
            url = share_url or f"https://www.yicai.com/news/{news_id}.html"

            author = item.get("NewsAuthor") or item.get("CreaterName") or "第一财经"
            summary = item.get("NewsNotes", "")
            published_at = item.get("CreateDate", "")  # ISO 格式

            # Try fetching desktop page for preview content
            content_raw = ""
            try:
                desk_url = url.replace("m.yicai.com", "www.yicai.com")
                dr = self._get(desk_url, timeout=10)
                dr.encoding = dr.apparent_encoding or "utf-8"
                soup = BeautifulSoup(dr.text, "lxml")
                art_block = soup.find("article")
                if not art_block:
                    art_block = soup.find("div", class_="g-bd")
                if art_block:
                    content_raw = art_block.get_text(separator="\n", strip=True)
            except Exception:
                pass

            articles.append(self._build_article(
                title=title,
                url=url,
                author=author,
                summary=summary,
                content_raw=content_raw[:2000],
                published_at=published_at,
            ))

        return articles
