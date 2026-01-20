"""飞书 Webhook 通知"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


class FeishuNotifier:
    """发送飞书 Webhook 通知"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        初始化飞书通知器

        Args:
            webhook_url: 飞书机器人 Webhook URL，如果为空则从环境变量读取
        """
        self.webhook_url = webhook_url or os.environ.get("FEISHU_WEBHOOK_URL", "")

    def send_report(
        self,
        summary: str,
        articles: List[Dict[str, Any]],
        report_url: Optional[str] = None,
        leaderboard: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        发送日报通知

        Args:
            summary: AI 生成的总结
            articles: 文章列表
            report_url: 日报链接（GitHub Pages 或仓库链接）
            leaderboard: 排行榜数据

        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("[Feishu] Webhook URL 未配置，跳过通知")
            return False

        # 构建卡片消息
        card = self._build_card(summary, articles, report_url, leaderboard)

        payload = {"msg_type": "interactive", "card": card}

        try:
            response = requests.post(
                self.webhook_url, json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 0:
                print("[Feishu] 通知发送成功")
                return True
            else:
                print(f"[Feishu] 通知发送失败: {result}")
                return False

        except Exception as e:
            print(f"[Feishu] 通知发送异常: {e}")
            return False

    def _build_card(
        self,
        summary: str,
        articles: List[Dict[str, Any]],
        report_url: Optional[str] = None,
        leaderboard: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        构建飞书卡片消息

        Args:
            summary: AI 总结
            articles: 文章列表
            report_url: 日报链接
            leaderboard: 排行榜数据

        Returns:
            卡片消息结构
        """
        date_str = datetime.now().strftime("%Y-%m-%d")

        # 卡片元素
        elements = []

        # 1. 总结部分
        elements.append({
            "tag": "markdown",
            "content": summary,
        })

        # 2. 分隔线
        elements.append({"tag": "hr"})

        # 3. 排行榜（如果有）
        if leaderboard:
            leaderboard_content = self._format_leaderboard(leaderboard)
            if leaderboard_content:
                elements.append({
                    "tag": "markdown",
                    "content": leaderboard_content,
                })
                elements.append({"tag": "hr"})

        # 4. 资讯列表（展开显示，最多 5 条）
        if articles:
            elements.append({
                "tag": "markdown",
                "content": "**📰 详细资讯**",
            })

            for article in articles[:5]:
                title = article.get("title", "无标题")
                link = article.get("link", "")
                source = article.get("source", "")
                summary_text = article.get("summary", "")[:150]  # 截取摘要
                pub_time = ""
                if article.get("published"):
                    pub_time = article["published"].strftime("%H:%M")

                # 每篇文章一个 markdown 块
                article_content = f"**[{title}]({link})**\n"
                article_content += f"*{source}*"
                if pub_time:
                    article_content += f" | *{pub_time}*"
                if summary_text:
                    article_content += f"\n{summary_text}..."

                elements.append({
                    "tag": "markdown",
                    "content": article_content,
                })

            if len(articles) > 5:
                elements.append({
                    "tag": "markdown",
                    "content": f"*... 共 {len(articles)} 条资讯*",
                })

        # 5. 查看完整日报按钮
        if report_url:
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "查看完整日报"},
                        "type": "primary",
                        "url": report_url,
                    }
                ],
            })

        # 构建卡片
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🤖 {date_str} 国产大模型日报",
                },
                "template": "blue",
            },
            "elements": elements,
        }

        return card

    def _format_leaderboard(self, leaderboard: Dict[str, Any]) -> str:
        """格式化排行榜为飞书 markdown"""
        lines = ["**📊 国产模型排行榜 (LM Arena)**\n"]

        # 全球 Top 5
        top_global = leaderboard.get("top_global", [])
        if top_global:
            lines.append("**全球 Top 5**")
            for model in top_global[:5]:
                name = model.get("model_name", "Unknown")
                if len(name) > 30:
                    name = name[:27] + "..."
                elo = model.get("elo_score", 0)
                rank = model.get("rank", "-")
                lines.append(f"{rank}. {name} ({elo:.0f})")
            lines.append("")

        # 国产模型
        chinese_models = leaderboard.get("chinese_models", [])
        if chinese_models:
            lines.append("**国产模型 Top 5**")
            for model in chinese_models[:5]:
                name = model.get("model_name", "Unknown")
                if len(name) > 30:
                    name = name[:27] + "..."
                elo = model.get("elo_score", 0)
                rank = model.get("rank", "-")
                lines.append(f"#{rank} {name} ({elo:.0f})")

        return "\n".join(lines)

    def send_text(self, text: str) -> bool:
        """
        发送纯文本消息（备用方法）

        Args:
            text: 消息文本

        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("[Feishu] Webhook URL 未配置，跳过通知")
            return False

        payload = {"msg_type": "text", "content": {"text": text}}

        try:
            response = requests.post(
                self.webhook_url, json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json().get("code") == 0
        except Exception as e:
            print(f"[Feishu] 发送失败: {e}")
            return False
