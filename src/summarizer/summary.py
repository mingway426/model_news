"""AI Summarizer - 使用智谱 GLM 生成资讯总结"""

from typing import List, Dict, Any, Optional
from .glm_client import GLMClient


class Summarizer:
    """使用智谱 GLM 生成资讯总结"""

    SYSTEM_PROMPT = """你是一个专业的 AI 资讯分析师，专注于国产大模型领域。
你的任务是分析当日的 AI 资讯，并生成简洁的中文摘要。

要求：
1. 总结要点：提炼 3-5 条最重要的资讯要点
2. 语言简洁：每条要点不超过 50 字
3. 突出重点：优先关注模型发布、技术突破、重要合作等
4. 客观中立：只陈述事实，不添加主观评价"""

    SUMMARY_PROMPT_TEMPLATE = """以下是今日收集的 AI 资讯列表：

{articles_text}

请根据以上资讯，生成今日要点总结。格式如下：

## 今日要点

1. [要点1]
2. [要点2]
3. [要点3]
...

如果资讯较少或没有特别重要的内容，可以适当减少要点数量。"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化总结器

        Args:
            api_key: 智谱 API 密钥
        """
        self.client = GLMClient(api_key)

    def summarize(self, articles: List[Dict[str, Any]]) -> str:
        """
        生成资讯总结

        Args:
            articles: 文章列表

        Returns:
            总结文本
        """
        if not articles:
            return "## 今日要点\n\n暂无相关资讯。"

        # 构建文章列表文本
        articles_text = self._build_articles_text(articles)

        # 构建 prompt
        prompt = self.SUMMARY_PROMPT_TEMPLATE.format(articles_text=articles_text)

        # 调用 GLM 生成总结
        print("[Summarizer] 正在生成 AI 总结...")
        try:
            summary = self.client.chat(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.5,  # 较低的温度以获得更稳定的输出
            )
            print("[Summarizer] 总结生成完成")
            return summary
        except Exception as e:
            print(f"[Summarizer] 总结生成失败: {e}")
            return "## 今日要点\n\n总结生成失败，请查看详细资讯列表。"

    def _build_articles_text(self, articles: List[Dict[str, Any]]) -> str:
        """
        将文章列表转换为文本

        Args:
            articles: 文章列表

        Returns:
            格式化的文章列表文本
        """
        lines = []
        for i, article in enumerate(articles[:20], 1):  # 最多取 20 篇避免超长
            title = article.get("title", "无标题")
            summary = article.get("summary", "")[:200]  # 截断摘要
            source = article.get("source", "未知来源")

            lines.append(f"{i}. 【{source}】{title}")
            if summary:
                lines.append(f"   摘要：{summary}")
            lines.append("")

        return "\n".join(lines)
