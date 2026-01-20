"""Data Aggregator - 聚合多数据源"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import yaml
import os

from .rss_fetcher import RSSFetcher
from .gnews_fetcher import GNewsFetcher


class Aggregator:
    """聚合多个数据源的文章"""

    def __init__(
        self,
        config_path: str = "config/sources.yaml",
        gnews_api_key: Optional[str] = None,
    ):
        """
        初始化聚合器

        Args:
            config_path: 配置文件路径
            gnews_api_key: GNews API 密钥
        """
        self.config = self._load_config(config_path)
        self.rss_fetcher = RSSFetcher(self.config.get("rss_sources", []))
        self.gnews_fetcher = GNewsFetcher(gnews_api_key)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_path = os.path.join(root_dir, config_path)

        if not os.path.exists(full_path):
            print(f"[Aggregator] 配置文件不存在: {full_path}，使用默认配置")
            return {"rss_sources": [], "default_topics": []}

        with open(full_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def fetch_all(self, topics: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        从所有数据源抓取文章

        Args:
            topics: 搜索主题列表（用于 GNews），如果为空则使用配置文件中的默认主题

        Returns:
            按时间排序的文章列表
        """
        all_articles = []

        # 1. 抓取 RSS
        print("\n=== 开始抓取 RSS ===")
        rss_articles = self.rss_fetcher.fetch_all()
        all_articles.extend(rss_articles)
        print(f"RSS 总计: {len(rss_articles)} 篇\n")

        # 2. 抓取 GNews
        print("=== 开始抓取 GNews ===")
        search_topics = topics or self.config.get("default_topics", [])
        if search_topics:
            gnews_articles = self.gnews_fetcher.fetch_by_keywords(search_topics)
            all_articles.extend(gnews_articles)
            print(f"GNews 总计: {len(gnews_articles)} 篇\n")

        # 3. 按时间排序（最新的在前）
        all_articles = self._sort_by_date(all_articles)

        print(f"=== 抓取完成，共 {len(all_articles)} 篇文章 ===\n")
        return all_articles

    def _sort_by_date(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按发布时间降序排序"""

        def get_date(article: Dict) -> datetime:
            pub_date = article.get("published")
            if pub_date:
                return pub_date
            return datetime.min

        return sorted(articles, key=get_date, reverse=True)
