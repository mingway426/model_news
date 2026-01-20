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

    # 默认大模型相关关键词
    DEFAULT_TOPICS = [
        # 国产模型品牌
        "DeepSeek", "深度求索",
        "Qwen", "通义千问", "阿里云",
        "GLM", "智谱", "ChatGLM",
        "Kimi", "Moonshot", "月之暗面",
        "豆包", "字节", "火山引擎",
        "文心一言", "百度", "ERNIE",
        "混元", "腾讯",
        "MiniMax", "海螺",
        "百川", "Baichuan",
        "零一万物", "Yi",
        "阶跃星辰", "Step",
        "商汤", "SenseChat",
        # 国际模型
        "GPT", "OpenAI", "ChatGPT",
        "Claude", "Anthropic",
        "Gemini", "Google",
        "Llama", "Meta",
        # 通用 AI 关键词
        "大模型", "LLM", "大语言模型",
        "AI", "人工智能", "机器学习",
        "AGI", "通用人工智能",
        "推理模型", "Reasoning",
        "多模态", "视觉语言",
        "AI Agent", "智能体",
        "RAG", "向量数据库",
        "微调", "Fine-tune",
        "RLHF", "强化学习",
    ]

    def __init__(self, topics: Optional[List[str]] = None):
        """
        初始化过滤器

        Args:
            topics: 关键词列表，如果为空则从环境变量或默认列表读取
        """
        self.topics = topics or self._load_topics_from_env() or self.DEFAULT_TOPICS

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
