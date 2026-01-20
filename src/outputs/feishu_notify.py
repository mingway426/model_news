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
    ) -> bool:
        """
        发送日报通知

        Args:
            summary: AI 生成的总结
            articles: 文章列表
            report_url: 日报链接（GitHub Pages 或仓库链接）

        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("[Feishu] Webhook URL 未配置，跳过通知")
            return False

        # 构建卡片消息
        card = self._build_card(summary, articles, report_url)

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
    ) -> Dict[str, Any]:
        """
        构建飞书卡片消息

        Args:
            summary: AI 总结
            articles: 文章列表
            report_url: 日报链接

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

        # 3. 资讯列表（最多显示 5 条）
        if articles:
            article_lines = ["**📰 详细资讯**\n"]
            for article in articles[:5]:
                title = article.get("title", "无标题")
                link = article.get("link", "")
                source = article.get("source", "")
                if link:
                    article_lines.append(f"• [{title}]({link}) *{source}*")
                else:
                    article_lines.append(f"• {title} *{source}*")

            if len(articles) > 5:
                article_lines.append(f"\n*... 共 {len(articles)} 条资讯*")

            elements.append({
                "tag": "markdown",
                "content": "\n".join(article_lines),
            })

        # 4. 查看完整日报按钮
        if report_url:
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
