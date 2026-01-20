"""智谱 GLM API Client"""

import os
import requests
from typing import Optional


class GLMClient:
    """智谱 GLM API 客户端"""

    BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智谱客户端

        Args:
            api_key: 智谱 API 密钥，如果为空则从环境变量 GLM_API_KEY 读取
        """
        self.api_key = api_key or os.environ.get("GLM_API_KEY", "")
        if not self.api_key:
            raise ValueError("GLM_API_KEY 未配置")

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "glm-4-flash",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        调用智谱 GLM 进行对话

        Args:
            prompt: 用户输入
            system_prompt: 系统提示词
            model: 模型名称，默认使用免费的 glm-4-flash
            max_tokens: 最大输出 token 数
            temperature: 温度参数

        Returns:
            模型回复内容
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        response = requests.post(
            self.BASE_URL, headers=headers, json=data, timeout=60
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]
