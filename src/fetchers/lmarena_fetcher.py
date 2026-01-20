"""LM Arena Leaderboard Fetcher"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class LMArenaFetcher:
    """从 LM Arena 获取排行数据（通过 lmarena-history 项目）"""

    # JSON 数据地址
    DATA_URL = "https://raw.githubusercontent.com/nakasyou/lmarena-history/main/output/scores.json"

    # 国产模型关键词
    CHINESE_MODEL_KEYWORDS = [
        "deepseek",
        "qwen",
        "glm",
        "zhipu",
        "chatglm",
        "baichuan",
        "yi-",
        "internlm",
        "minimax",
        "moonshot",
        "kimi",
        "doubao",
        "ernie",
        "hunyuan",
        "sensechat",
        "step",
        "alibaba",
        "abab",
    ]

    def __init__(self):
        """初始化"""
        self._data = None

    def _load_data(self) -> Optional[Dict]:
        """加载 LM Arena 数据，返回最新日期的 text/overall 数据"""
        if self._data is not None:
            return self._data

        try:
            print("[LMArena] 正在加载 LM Arena 排行榜数据...")
            response = requests.get(self.DATA_URL, timeout=30)
            response.raise_for_status()
            raw_data = response.json()

            # 数据结构是 {date: {text: {...}, vision: {...}}}
            # 获取最新日期的数据
            dates = sorted(raw_data.keys(), reverse=True)
            if not dates:
                print("[LMArena] 无数据")
                return None

            latest_date = dates[0]
            print(f"[LMArena] 使用最新数据: {latest_date}")

            latest_data = raw_data[latest_date]
            # 提取 text -> overall 数据
            text_data = latest_data.get("text", {})
            overall_data = text_data.get("overall", {})

            # 转换为统一格式 {model_name: score}
            self._data = {"overall": overall_data, "date": latest_date}
            print(f"[LMArena] 加载完成，共 {len(overall_data)} 个模型")
            return self._data
        except Exception as e:
            print(f"[LMArena] 加载失败: {e}")
            return None

    def fetch_overall_ranking(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        获取总体排名

        Args:
            top_n: 返回前 N 名

        Returns:
            模型列表，包含 model_name, elo_score, rank
        """
        data = self._load_data()
        if not data or "overall" not in data:
            return []

        overall = data["overall"]
        models = []

        for model_id, score in overall.items():
            # 数据格式是 {model_name: elo_score}
            if isinstance(score, (int, float)):
                models.append({
                    "model_name": model_id,
                    "elo_score": score,
                })

        # 按 ELO 分数排序
        models.sort(key=lambda x: x.get("elo_score", 0), reverse=True)

        # 添加排名
        for i, model in enumerate(models, 1):
            model["rank"] = i

        return models[:top_n]

    def fetch_chinese_models(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取国产模型排名

        Args:
            top_n: 返回前 N 名

        Returns:
            国产模型列表
        """
        all_models = self.fetch_overall_ranking(top_n=500)  # 获取更多以找到国产模型

        chinese_models = []
        for model in all_models:
            model_name = model.get("model_name", "").lower()
            if self._is_chinese_model(model_name):
                chinese_models.append(model)

        print(f"[LMArena] 找到 {len(chinese_models)} 个国产模型")
        return chinese_models[:top_n]

    def _is_chinese_model(self, model_name: str) -> bool:
        """判断是否为国产模型"""
        model_name_lower = model_name.lower()
        return any(keyword in model_name_lower for keyword in self.CHINESE_MODEL_KEYWORDS)

    def fetch_category_ranking(self, category: str = "overall", top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取特定类别的排名

        Args:
            category: 类别名称 (overall)
            top_n: 返回前 N 名

        Returns:
            模型列表
        """
        # 当前实现只支持 overall
        if category != "overall":
            print(f"[LMArena] 当前只支持 'overall' 类别")
            return []

        return self.fetch_overall_ranking(top_n=top_n)

    def get_leaderboard_summary(self, top_n: int = 10) -> Dict[str, Any]:
        """
        获取排行榜摘要

        Args:
            top_n: 国产模型显示前 N 名

        Returns:
            排行榜摘要
        """
        chinese_models = self.fetch_chinese_models(top_n=top_n)
        top_global = self.fetch_overall_ranking(top_n=5)

        return {
            "chinese_models": chinese_models,
            "top_global": top_global,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": "LM Arena (lmarena.ai)",
        }
