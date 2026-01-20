"""Keyword Filter - 关键词过滤"""

import os
import json
from typing import List, Dict, Any, Optional


class KeywordFilter:
    """基于关键词过滤文章"""

    def __init__(self, topics: Optional[List[str]] = None):
        """
        初始化过滤器

        Args:
            topics: 关键词列表，如果为空则从环境变量 SEARCH_TOPICS 读取
        """
        self.topics = topics or self._load_topics_from_env()

    def _load_topics_from_env(self) -> List[str]:
        """从环境变量加载搜索主题"""
        topics_str = os.environ.get("SEARCH_TOPICS", "")
        if not topics_str:
            return []

        try:
            topics = json.loads(topics_str)
            if isinstance(topics, list):
                return topics
        except json.JSONDecodeError:
            # 尝试逗号分隔格式
            return [t.strip() for t in topics_str.split(",") if t.strip()]

        return []

    def filter(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤匹配关键词的文章

        Args:
            articles: 原始文章列表

        Returns:
            匹配关键词的文章列表
        """
        if not self.topics:
            print("[Filter] 未配置关键词，返回所有文章")
            return articles

        filtered = []
        for article in articles:
            if self._matches_any_topic(article):
                filtered.append(article)

        print(f"[Filter] 关键词匹配: {len(filtered)}/{len(articles)} 篇")
        return filtered

    def _matches_any_topic(self, article: Dict[str, Any]) -> bool:
        """
        检查文章是否匹配任意关键词

        Args:
            article: 文章

        Returns:
            是否匹配
        """
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        text = f"{title} {summary}"

        for topic in self.topics:
            if topic.lower() in text:
                return True

        return False

    def get_topics(self) -> List[str]:
        """返回当前配置的关键词列表"""
        return self.topics
