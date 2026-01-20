# AI News Tracker

自动追踪国产大模型资讯，每日生成 AI 总结日报并推送至飞书。

## 功能特性

- **多源数据抓取**：支持 RSS（机器之心、36Kr）和 GNews API
- **智能过滤**：基于关键词过滤相关资讯，自动去重
- **AI 总结**：使用智谱 GLM 生成每日要点总结
- **飞书通知**：通过 Webhook 推送卡片消息到飞书群
- **GitHub Action**：每天自动运行，无需服务器

## 快速开始

### 1. Fork 本仓库

### 2. 配置 GitHub Secrets

在仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加以下 Secrets：

| Secret 名称 | 必填 | 说明 | 示例 |
|------------|------|------|------|
| `GLM_API_KEY` | ✅ | 智谱 API 密钥 | 从 [智谱开放平台](https://open.bigmodel.cn/) 获取 |
| `FEISHU_WEBHOOK_URL` | ✅ | 飞书机器人 Webhook URL | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` |
| `SEARCH_TOPICS` | ✅ | 搜索主题（JSON 数组） | `["智谱","Kimi","MiniMax","DeepSeek","大模型"]` |
| `GNEWS_API_KEY` | ⚠️ 可选 | GNews API 密钥 | 从 [GNews.io](https://gnews.io/) 获取 |

### 3. 手动触发测试

在 `Actions` 页面，选择 `Daily AI News Tracker`，点击 `Run workflow` 手动触发。

### 4. 自动运行

配置完成后，Action 将在每天北京时间 9:00 自动运行。

## 项目结构

```
ai-news-tracker/
├── .github/workflows/
│   └── daily-news.yml      # GitHub Action 配置
├── src/
│   ├── main.py             # 主程序入口
│   ├── fetchers/           # 数据抓取模块
│   │   ├── rss_fetcher.py  # RSS 抓取器
│   │   ├── gnews_fetcher.py# GNews API 抓取器
│   │   └── aggregator.py   # 数据聚合器
│   ├── processors/         # 数据处理模块
│   │   ├── dedup.py        # 去重
│   │   └── filter.py       # 关键词过滤
│   ├── summarizer/         # AI 总结模块
│   │   ├── glm_client.py   # 智谱 API 客户端
│   │   └── summary.py      # 总结生成
│   └── outputs/            # 输出模块
│       ├── markdown_report.py  # Markdown 日报
│       └── feishu_notify.py    # 飞书通知
├── config/
│   └── sources.yaml        # RSS 源配置
├── output/                 # 日报输出目录
├── requirements.txt
└── README.md
```

## 本地开发

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

### 3. 运行

```bash
python src/main.py
```

## 数据源

### RSS 源（免费、稳定）

| 来源 | 说明 |
|-----|------|
| 机器之心 | AI 技术深度报道 |
| 36Kr | 科技行业资讯 |
| 新智元 | AI 领域资讯（第三方 RSS） |

### GNews API（可选）

- 免费额度：100 次/天
- 支持中文关键词搜索
- 注册地址：https://gnews.io/

## 自定义配置

### 修改 RSS 源

编辑 `config/sources.yaml`：

```yaml
rss_sources:
  - name: 机器之心
    url: https://www.jiqizhixin.com/rss
    enabled: true
```

### 修改搜索主题

通过 GitHub Secret `SEARCH_TOPICS` 配置，支持两种格式：

```
# JSON 数组格式
["智谱", "Kimi", "大模型"]

# 逗号分隔格式
智谱,Kimi,大模型
```

### 修改运行时间

编辑 `.github/workflows/daily-news.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 时间，北京时间 +8
```

## License

MIT
