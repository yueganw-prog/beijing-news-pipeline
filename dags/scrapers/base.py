"""新闻爬虫基类 — HTTP 请求、重试、文章格式化。"""
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# 新浪财经 JSONP 回调函数名
JSONP_RE = re.compile(r"^[a-zA-Z_]\w*\s*\((.+)\)\s*$", re.DOTALL)


class ScraperError(Exception):
    """爬虫异常基类。"""


class BaseScraper:
    """新闻爬虫基类。

    封装 Session 管理、重试策略、article 格式化。
    子类只需实现 ``fetch()`` 方法。
    """

    source_id: str = ""
    category: str = ""

    def __init__(self, source_id: str = "", category: str = "",
                 timeout: int = 30, max_retries: int = 3):
        self.source_id = source_id
        self.category = category
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._build_session()

    # ── HTTP 会话 ──────────────────────────────────
    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)
        retry = Retry(
            total=self.max_retries,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get(self, url: str, **kwargs) -> requests.Response:
        logger.info("GET %s", url)
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        return resp

    def _get_json(self, url: str, **kwargs) -> dict:
        resp = self._get(url, **kwargs)
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.json()

    def _get_jsonp(self, url: str, **kwargs) -> dict:
        """解析 JSONP 响应，去掉回调函数包裹。"""
        resp = self._get(url, **kwargs)
        resp.encoding = resp.apparent_encoding or "utf-8"
        raw = resp.text.strip()
        m = JSONP_RE.match(raw)
        if m:
            return json.loads(m.group(1))
        return json.loads(raw)

    # ── 子类接口 ───────────────────────────────────
    def fetch(self) -> List[Dict]:
        """返回标准 article 字典列表。子类必须实现。"""
        raise NotImplementedError

    # ── Article 构造 ──────────────────────────────
    def _build_article(
        self,
        title: str,
        url: str,
        author: str = "",
        summary: str = "",
        content_raw: str = "",
        published_at: Optional[str] = None,
    ) -> Dict:
        return {
            "source": self.source_id,
            "category": self.category,
            "title": title.strip(),
            "url": url.strip(),
            "author": author.strip() or "自动采集",
            "summary": summary.strip(),
            "content_raw": content_raw.strip(),
            "published_at": published_at or datetime.now().isoformat(),
        }
