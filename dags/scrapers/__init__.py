"""新闻爬虫调度模块 — 按 source_id 分发到对应爬虫。"""
import logging
from typing import Dict, List

from .base import BaseScraper, ScraperError

logger = logging.getLogger(__name__)

# 爬虫注册表：source_id -> 类路径
_SCRAPER_REGISTRY = {
    "sina_finance": "SinaFinanceScraper",
    "yicai": "YicaiScraper",
    "eeo": "EeoScraper",
    "36kr": "Kr36Scraper",
    "huxiu": "HuxiuScraper",
    "ithome": "IthomeScraper",
    "bjnews": "BjnewsScraper",
    "bjdaily": "BjdailyScraper",
    "bjbusiness": "BjbusinessScraper",
}


def _get_scraper_class(source_id: str):
    """延迟导入，按 source_id 返回爬虫类。"""
    cls_name = _SCRAPER_REGISTRY.get(source_id)
    if cls_name is None:
        raise ScraperError(f"Unknown source: {source_id}")
    if source_id == "sina_finance":
        from .sina_finance import SinaFinanceScraper
        return SinaFinanceScraper
    if source_id == "yicai":
        from .yicai import YicaiScraper
        return YicaiScraper
    if source_id == "eeo":
        from .eeo import EeoScraper
        return EeoScraper
    if source_id == "36kr":
        from .kr36 import Kr36Scraper
        return Kr36Scraper
    if source_id == "huxiu":
        from .huxiu import HuxiuScraper
        return HuxiuScraper
    if source_id == "bjnews":
        from .bjnews import BjnewsScraper
        return BjnewsScraper
    if source_id == "bjdaily":
        from .bjdaily import BjdailyScraper
        return BjdailyScraper
    if source_id == "bjbusiness":
        from .bjbusiness import BjbusinessScraper
        return BjbusinessScraper
    if source_id == "ithome":
        from .ithome import IthomeScraper
        return IthomeScraper
    raise ScraperError(f"No scraper registered for: {source_id}")

def fetch_source(source_id: str, category: str) -> List[Dict]:
    """按 source_id 分发到对应爬虫并返回文章列表。
    单个爬虫失败不阻塞其他爬虫，返回空列表并记录错误。
    """
    scraper_cls = _get_scraper_class(source_id)
    scraper = scraper_cls(source_id=source_id, category=category)
    logger.info("Scraper [%s/%s] starting", category, source_id)
    try:
        import signal
        articles = scraper.fetch()
        logger.info("Scraper [%s] returned %d articles", source_id, len(articles))
        return articles
    except Exception:
        logger.exception("Scraper [%s] failed, returning empty list", source_id)
        return []
