"""AI News Tracker - 主程序入口"""

import os
import sys
import json
from typing import List, Optional
from dotenv import load_dotenv

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetchers import Aggregator, LMArenaFetcher
from src.processors import Deduplicator, KeywordFilter, TimeFilter
from src.summarizer import Summarizer
from src.outputs import MarkdownReport, FeishuNotifier


def load_topics() -> Optional[List[str]]:
    """从环境变量加载搜索主题"""
    topics_str = os.environ.get("SEARCH_TOPICS", "")
    if not topics_str:
        return None

    try:
        topics = json.loads(topics_str)
        if isinstance(topics, list):
            return topics
    except json.JSONDecodeError:
        # 尝试逗号分隔格式
        return [t.strip() for t in topics_str.split(",") if t.strip()]

    return None


def main():
    """主程序"""
    # 加载环境变量（本地开发时使用 .env 文件）
    load_dotenv()

    print("=" * 50)
    print("AI News Tracker - 国产大模型资讯追踪")
    print("=" * 50)

    # 获取配置
    gnews_api_key = os.environ.get("GNEWS_API_KEY")
    glm_api_key = os.environ.get("GLM_API_KEY")
    feishu_webhook = os.environ.get("FEISHU_WEBHOOK_URL")
    topics = load_topics()

    print(f"\n配置信息:")
    print(f"  - GLM API: {'已配置' if glm_api_key else '未配置'}")
    print(f"  - GNews API: {'已配置' if gnews_api_key else '未配置（仅使用 RSS）'}")
    print(f"  - 飞书 Webhook: {'已配置' if feishu_webhook else '未配置'}")
    print(f"  - 搜索主题: {topics if topics else '使用默认配置'}")

    # 1. 抓取资讯
    print("\n" + "=" * 50)
    print("步骤 1: 抓取资讯")
    print("=" * 50)

    aggregator = Aggregator(gnews_api_key=gnews_api_key)
    articles = aggregator.fetch_all(topics=topics)

    if not articles:
        print("\n未抓取到任何文章，程序退出")
        return

    # 1.5 抓取排行榜数据
    print("\n" + "=" * 50)
    print("步骤 1.5: 获取模型排行榜")
    print("=" * 50)

    leaderboard_data = None
    try:
        lmarena_fetcher = LMArenaFetcher()
        leaderboard_data = lmarena_fetcher.get_leaderboard_summary(top_n=10)
        chinese_count = len(leaderboard_data.get("chinese_models", []))
        print(f"[Leaderboard] 获取到 {chinese_count} 个国产模型排名")
    except Exception as e:
        print(f"[Leaderboard] 获取失败: {e}")

    # 2. 数据处理
    print("\n" + "=" * 50)
    print("步骤 2: 数据处理")
    print("=" * 50)

    # 去重
    deduplicator = Deduplicator()
    articles = deduplicator.deduplicate(articles)

    # 时间过滤（只保留最近 24 小时内的文章）
    time_filter = TimeFilter(hours=24)
    articles = time_filter.filter(articles)

    # 关键词过滤
    keyword_filter = KeywordFilter(topics=topics)
    articles = keyword_filter.filter(articles)

    print(f"\n处理后文章数量: {len(articles)}")

    if not articles:
        print("\n过滤后无相关文章，程序退出")
        return

    # 3. AI 总结
    print("\n" + "=" * 50)
    print("步骤 3: 生成 AI 总结")
    print("=" * 50)

    if glm_api_key:
        summarizer = Summarizer(api_key=glm_api_key)
        summary = summarizer.summarize(articles)
    else:
        print("[Warning] GLM API 未配置，跳过 AI 总结")
        summary = "## 今日要点\n\n（AI 总结未生成，请配置 GLM_API_KEY）"

    print(f"\n总结预览:\n{summary[:200]}...")

    # 4. 生成日报
    print("\n" + "=" * 50)
    print("步骤 4: 生成日报")
    print("=" * 50)

    report = MarkdownReport()
    report_path = report.generate(articles, summary, leaderboard=leaderboard_data)

    # 5. 发送通知
    print("\n" + "=" * 50)
    print("步骤 5: 发送飞书通知")
    print("=" * 50)

    if feishu_webhook:
        notifier = FeishuNotifier(webhook_url=feishu_webhook)
        # 可以配置 GitHub Pages 链接
        report_url = os.environ.get("REPORT_URL")
        notifier.send_report(summary, articles, report_url, leaderboard=leaderboard_data)
    else:
        print("[Info] 飞书 Webhook 未配置，跳过通知")

    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)
    print(f"\n日报已保存至: {report_path}")


if __name__ == "__main__":
    main()
