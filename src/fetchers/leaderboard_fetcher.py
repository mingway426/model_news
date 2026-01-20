"""Hugging Face Open LLM Leaderboard Fetcher"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class LeaderboardFetcher:
    """从 Hugging Face Open LLM Leaderboard 获取排行数据"""

    # 国产模型关键词（用于过滤）
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
        "aquila",
        "tigerbot",
        "moss",
        "chinese",
        "alibaba",
        "tsinghua",
        "tencent",
        "baidu",
        "bytedance",
    ]

    def __init__(self):
        """初始化排行榜抓取器"""
        self._dataset = None

    def _load_dataset(self):
        """懒加载数据集"""
        if self._dataset is None:
            try:
                from datasets import load_dataset

                print("[Leaderboard] 正在加载 Hugging Face Open LLM Leaderboard 数据...")
                self._dataset = load_dataset(
                    "open-llm-leaderboard/contents",
                    split="train",
                )
                print(f"[Leaderboard] 加载完成，共 {len(self._dataset)} 个模型")
            except Exception as e:
                print(f"[Leaderboard] 加载失败: {e}")
                self._dataset = None
        return self._dataset

    def fetch_top_models(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        获取排名前 N 的模型

        Args:
            top_n: 返回前 N 名

        Returns:
            模型列表
        """
        dataset = self._load_dataset()
        if dataset is None:
            return []

        models = []
        for item in dataset:
            try:
                model_info = self._parse_model_info(item)
                if model_info:
                    models.append(model_info)
            except Exception:
                continue

        # 按平均分排序
        models.sort(key=lambda x: x.get("average_score", 0), reverse=True)

        return models[:top_n]

    def fetch_chinese_models(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取国产模型排行

        Args:
            top_n: 返回前 N 名

        Returns:
            国产模型列表
        """
        dataset = self._load_dataset()
        if dataset is None:
            return []

        chinese_models = []
        for item in dataset:
            try:
                model_info = self._parse_model_info(item)
                if model_info and self._is_chinese_model(model_info.get("model_name", "")):
                    chinese_models.append(model_info)
            except Exception:
                continue

        # 按平均分排序
        chinese_models.sort(key=lambda x: x.get("average_score", 0), reverse=True)

        print(f"[Leaderboard] 找到 {len(chinese_models)} 个国产模型")
        return chinese_models[:top_n]

    def _parse_model_info(self, item: Dict) -> Optional[Dict[str, Any]]:
        """解析模型信息"""
        # 数据集的字段可能会变化，尝试多种字段名
        model_name = item.get("fullname") or ""

        if not model_name:
            return None

        # 平均分字段名是 "Average ⬆️"
        average_score = self._safe_float(item.get("Average ⬆️"))

        return {
            "model_name": model_name,
            "average_score": average_score,
            "ifeval": self._safe_float(item.get("IFEval")),
            "bbh": self._safe_float(item.get("BBH")),
            "math": self._safe_float(item.get("MATH Lvl 5")),
            "gpqa": self._safe_float(item.get("GPQA")),
            "musr": self._safe_float(item.get("MUSR")),
            "mmlu_pro": self._safe_float(item.get("MMLU-PRO")),
            "architecture": item.get("Architecture") or "",
            "precision": item.get("Precision") or "",
            "params": item.get("#Params (B)") or "",
        }

    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _is_chinese_model(self, model_name: str) -> bool:
        """判断是否为国产模型"""
        model_name_lower = model_name.lower()
        return any(keyword in model_name_lower for keyword in self.CHINESE_MODEL_KEYWORDS)

    def get_leaderboard_summary(self, top_n: int = 10) -> Dict[str, Any]:
        """
        获取排行榜摘要（用于日报）

        Args:
            top_n: 国产模型显示前 N 名

        Returns:
            排行榜摘要
        """
        chinese_models = self.fetch_chinese_models(top_n=top_n)
        top_global = self.fetch_top_models(top_n=5)

        return {
            "chinese_models": chinese_models,
            "top_global": top_global,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": "Hugging Face Open LLM Leaderboard",
        }
