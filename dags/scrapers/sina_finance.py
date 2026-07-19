"""新浪财经爬虫 — feed API + 文章正文。"""
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from bs4 import BeautifulSoup

from .base import BaseScraper, ScraperError

logger = logging.getLogger(__name__)

# 滚动新闻 API
API_URL = "https://feed.mix.sina.com.cn/api/roll/get"
API_PARAMS = {
    "pageid": "153",
    "lid": "2509",   # 财经频道
    "k": "",
    "num": "50",
    "page": "1",
}

TZ_BEIJING = timezone(timedelta(hours=8))


def _ts_to_iso(ts: str) -> str:
    """Unix 秒级时间戳 -> ISO 8601。"""
    try:
        dt = datetime.fromtimestamp(int(ts), tz=TZ_BEIJING)
        return dt.isoformat()
    except (ValueError, TypeError):
        return datetime.now(TZ_BEIJING).isoformat()


class SinaFinanceScraper(BaseScraper):
    """新浪财经新闻爬虫。"""

    source_id = "sina_finance"
    category = "finance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self) -> List[Dict]:
        """从滚动新闻 API 获取文章列表，并抓取正文。"""
        resp = self._get_json(API_URL, params=API_PARAMS)
        result = resp.get("result", {})
        if result.get("status", {}).get("code") != 0:
            raise ScraperError(
                f"新浪 API 返回错误: {result.get('status')}"
            )
        items = result.get("data", [])
        logger.info("新浪财经 API 返回 %d 篇文章", len(items))

        articles = []
        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            if not title or not url:
                continue

            summary = item.get("intro", "")
            author = item.get("media_name", "新浪财经")
            published_at = _ts_to_iso(item.get("ctime", ""))

            # 尝试获取正文
            content_raw = ""
            try:
                content_raw = self._fetch_article_content(url)
            except Exception:
                logger.warning("抓取文章正文失败: %s", url)

            articles.append(self._build_article(
                title=title,
                url=url,
                author=author,
                summary=summary,
                content_raw=content_raw,
                published_at=published_at,
            ))

        return articles

    def _fetch_article_content(self, url: str) -> str:
        """抓取单篇文章正文。"""
        resp = self._get(url)
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        # 新浪文章正文在 article 或 .article-content 中
        art = soup.find("article")
        if not art:
            art = soup.find("div", class_="article-content")
        if not art:
            art = soup.find("div", class_="article")
        if not art:
            art = soup.find("div", id="article")
        if not art:
            art = soup.find("div", class_="art_pic_card")

        if art:
            # 移除 script / style / 广告
            for t in art.find_all(["script", "style", "ins"]):
                t.decompose()
            text = art.get_text(separator="\n", strip=True)
            return text[:5000]
        return ""
