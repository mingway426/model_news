"""Keyword Filter - 关键词过滤和时间过滤"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class TimeFilter:
    """基于时间过滤文章"""

    def __init__(self, hours: int = 24):
        """
        初始化时间过滤器

        Args:
            hours: 保留最近多少小时内的文章，默认 24 小时
        """
        self.hours = hours

    def filter(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤指定时间范围内的文章

        Args:
            articles: 原始文章列表

        Returns:
            时间范围内的文章列表
        """
        if not articles:
            return []

        cutoff_time = datetime.now() - timedelta(hours=self.hours)
        filtered = []
        no_date_count = 0

        for article in articles:
            pub_date = article.get("published")
            if pub_date is None:
                # 没有发布时间的文章保留（可能是解析问题）
                no_date_count += 1
                filtered.append(article)
            else:
                # 处理时区问题：将 offset-aware datetime 转换为 offset-naive
                if pub_date.tzinfo is not None:
                    pub_date = pub_date.replace(tzinfo=None)
                if pub_date >= cutoff_time:
                    filtered.append(article)

        excluded = len(articles) - len(filtered)
        print(f"[TimeFilter] 保留 {self.hours} 小时内文章: {len(filtered)}/{len(articles)} 篇（排除 {excluded} 篇过时文章）")
        if no_date_count > 0:
            print(f"[TimeFilter] 注意: {no_date_count} 篇文章无发布时间，已保留")

        return filtered


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
