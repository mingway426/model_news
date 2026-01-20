"""Markdown Report Generator - 生成 Markdown 格式日报"""

import os
from datetime import datetime
from typing import List, Dict, Any


class MarkdownReport:
    """生成 Markdown 格式的日报"""

    def __init__(self, output_dir: str = "output"):
        """
        初始化日报生成器

        Args:
            output_dir: 输出目录
        """
        # 获取项目根目录
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.output_dir = os.path.join(root_dir, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(
        self,
        articles: List[Dict[str, Any]],
        summary: str,
        date: datetime = None,
    ) -> str:
        """
        生成日报并保存

        Args:
            articles: 文章列表
            summary: AI 生成的总结
            date: 日期，默认今天

        Returns:
            生成的文件路径
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")
        filename = f"{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)

        content = self._build_content(articles, summary, date_str)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[Report] 日报已保存: {filepath}")
        return filepath

    def _build_content(
        self,
        articles: List[Dict[str, Any]],
        summary: str,
        date_str: str,
    ) -> str:
        """
        构建 Markdown 内容

        Args:
            articles: 文章列表
            summary: AI 总结
            date_str: 日期字符串

        Returns:
            Markdown 内容
        """
        lines = [
            f"# {date_str} 国产大模型日报",
            "",
            summary,
            "",
            "---",
            "",
            "## 详细资讯",
            "",
        ]

        if not articles:
            lines.append("暂无相关资讯。")
        else:
            for article in articles:
                lines.extend(self._format_article(article))

        lines.extend([
            "",
            "---",
            "",
            f"*本日报由 AI News Tracker 自动生成，更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        ])

        return "\n".join(lines)

    def _format_article(self, article: Dict[str, Any]) -> List[str]:
        """
        格式化单篇文章

        Args:
            article: 文章数据

        Returns:
            Markdown 行列表
        """
        title = article.get("title", "无标题")
        link = article.get("link", "")
        summary = article.get("summary", "")[:300]  # 截断摘要
        source = article.get("source", "未知来源")
        published = article.get("published")

        lines = [f"### {title}", ""]

        # 元信息
        meta_parts = [f"**来源**: {source}"]
        if published:
            meta_parts.append(f"**时间**: {published.strftime('%Y-%m-%d %H:%M')}")
        lines.append(" | ".join(meta_parts))
        lines.append("")

        # 摘要
        if summary:
            lines.append(summary)
            lines.append("")

        # 链接
        if link:
            lines.append(f"[阅读原文]({link})")
            lines.append("")

        return lines

    def get_latest_report_path(self) -> str:
        """获取最新日报的路径"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.output_dir, f"{date_str}.md")
