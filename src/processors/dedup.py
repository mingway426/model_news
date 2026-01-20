"""Deduplicator - 文章去重"""

from typing import List, Dict, Any
from urllib.parse import urlparse


class Deduplicator:
    """基于 URL 和标题相似度去重"""

    def __init__(self, similarity_threshold: float = 0.8):
        """
        初始化去重器

        Args:
            similarity_threshold: 标题相似度阈值（0-1），超过此值视为重复
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对文章列表去重

        Args:
            articles: 原始文章列表

        Returns:
            去重后的文章列表
        """
        if not articles:
            return []

        seen_urls = set()
        seen_titles = []
        unique_articles = []

        for article in articles:
            # 1. URL 去重
            normalized_url = self._normalize_url(article.get("link", ""))
            if normalized_url in seen_urls:
                continue

            # 2. 标题相似度去重
            title = article.get("title", "")
            if self._is_similar_title(title, seen_titles):
                continue

            # 添加到结果
            seen_urls.add(normalized_url)
            seen_titles.append(title)
            unique_articles.append(article)

        removed_count = len(articles) - len(unique_articles)
        if removed_count > 0:
            print(f"[Dedup] 去除 {removed_count} 篇重复文章")

        return unique_articles

    def _normalize_url(self, url: str) -> str:
        """
        标准化 URL，去除追踪参数等

        Args:
            url: 原始 URL

        Returns:
            标准化后的 URL
        """
        if not url:
            return ""

        parsed = urlparse(url)
        # 只保留 scheme + netloc + path
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # 去除末尾斜杠
        return normalized.rstrip("/")

    def _is_similar_title(self, title: str, seen_titles: List[str]) -> bool:
        """
        检查标题是否与已有标题相似

        Args:
            title: 待检查的标题
            seen_titles: 已有标题列表

        Returns:
            是否相似
        """
        if not title:
            return False

        for seen_title in seen_titles:
            similarity = self._calculate_similarity(title, seen_title)
            if similarity >= self.similarity_threshold:
                return True

        return False

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """
        计算两个字符串的相似度（Jaccard 系数）

        Args:
            s1: 字符串 1
            s2: 字符串 2

        Returns:
            相似度（0-1）
        """
        if not s1 or not s2:
            return 0.0

        # 使用字符级别的 Jaccard 系数
        set1 = set(s1)
        set2 = set(s2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union
