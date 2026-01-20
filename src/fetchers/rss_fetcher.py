"""RSS Feed Fetcher"""

import feedparser
from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser
import html
import re


class RSSFetcher:
    """从 RSS 源抓取文章"""

    def __init__(self, sources: List[Dict[str, Any]]):
        """
        初始化 RSS 抓取器

        Args:
            sources: RSS 源列表，每个元素包含 name, url, enabled
        """
        self.sources = [s for s in sources if s.get("enabled", True)]

    def fetch_all(self) -> List[Dict[str, Any]]:
        """
        抓取所有 RSS 源的文章

        Returns:
            文章列表，每篇文章包含 title, summary, link, published, source
        """
        all_articles = []
        for source in self.sources:
            try:
                articles = self._fetch_source(source)
                all_articles.extend(articles)
                print(f"[RSS] {source['name']}: 获取 {len(articles)} 篇文章")
            except Exception as e:
                print(f"[RSS] {source['name']}: 抓取失败 - {e}")
        return all_articles

    def _fetch_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        抓取单个 RSS 源

        Args:
            source: RSS 源配置

        Returns:
            文章列表
        """
        feed = feedparser.parse(source["url"])
        articles = []

        for entry in feed.entries:
            article = {
                "title": self._clean_text(entry.get("title", "")),
                "summary": self._extract_summary(entry),
                "link": entry.get("link", ""),
                "published": self._parse_date(entry),
                "source": source["name"],
            }
            if article["title"] and article["link"]:
                articles.append(article)

        return articles

    def _extract_summary(self, entry: Dict) -> str:
        """
        提取文章摘要

        优先使用 content:encoded，其次 summary，最后 description
        """
        # 尝试从 content:encoded 获取全文（机器之心使用这个字段）
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
            return self._clean_text(content)[:500]

        # 尝试 summary
        summary = entry.get("summary", "")
        if summary:
            return self._clean_text(summary)[:500]

        # 尝试 description
        description = entry.get("description", "")
        return self._clean_text(description)[:500]

    def _clean_text(self, text: str) -> str:
        """清理 HTML 标签和多余空白"""
        if not text:
            return ""
        # 移除 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)
        # 解码 HTML 实体
        text = html.unescape(text)
        # 合并多余空白
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _parse_date(self, entry: Dict) -> Optional[datetime]:
        """解析发布日期"""
        # 尝试多个日期字段
        date_fields = ["published", "updated", "created"]
        for field in date_fields:
            date_str = entry.get(field)
            if date_str:
                try:
                    return date_parser.parse(date_str)
                except Exception:
                    continue
        return None
