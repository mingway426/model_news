"""GNews API Fetcher"""

import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser


class GNewsFetcher:
    """从 GNews API 抓取新闻"""

    BASE_URL = "https://gnews.io/api/v4/search"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 GNews 抓取器

        Args:
            api_key: GNews API 密钥，如果为空则跳过 API 搜索
        """
        self.api_key = api_key

    def fetch_by_keywords(
        self, keywords: List[str], max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        按关键词搜索新闻

        Args:
            keywords: 搜索关键词列表
            max_results: 每个关键词返回的最大结果数

        Returns:
            文章列表
        """
        if not self.api_key:
            print("[GNews] API Key 未配置，跳过 GNews 搜索")
            return []

        all_articles = []
        for keyword in keywords:
            try:
                articles = self._search(keyword, max_results)
                all_articles.extend(articles)
                print(f"[GNews] '{keyword}': 获取 {len(articles)} 篇文章")
            except Exception as e:
                print(f"[GNews] '{keyword}': 搜索失败 - {e}")

        return all_articles

    def _search(self, keyword: str, max_results: int) -> List[Dict[str, Any]]:
        """
        搜索单个关键词

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            文章列表
        """
        params = {
            "q": keyword,
            "lang": "zh",  # 中文
            "max": min(max_results, 10),  # 免费版最多 10 条
            "apikey": self.api_key,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        articles = []

        for item in data.get("articles", []):
            article = {
                "title": item.get("title", ""),
                "summary": item.get("description", "")[:500] if item.get("description") else "",
                "link": item.get("url", ""),
                "published": self._parse_date(item.get("publishedAt")),
                "source": f"GNews/{item.get('source', {}).get('name', 'Unknown')}",
            }
            if article["title"] and article["link"]:
                articles.append(article)

        return articles

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        try:
            return date_parser.parse(date_str)
        except Exception:
            return None
