"""
Ollama客户端封装
"""
import asyncio
import json
from typing import Optional, List, Dict, Any
import aiohttp
from loguru import logger
from config import settings


class OllamaClient:
    """Ollama API客户端"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = aiohttp.ClientTimeout(total=120)  # 2分钟超时
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户提示词
            system: 系统提示词
            temperature: 温度参数（0-1）
            max_tokens: 最大token数
            stream: 是否流式输出
        
        Returns:
            生成的文本
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                }
            }
            
            if system:
                payload["system"] = system
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        if stream:
                            # 流式输出
                            full_response = ""
                            async for line in response.content:
                                if line:
                                    data = json.loads(line)
                                    if "response" in data:
                                        full_response += data["response"]
                            return full_response
                        else:
                            # 非流式输出
                            result = await response.json()
                            return result.get("response", "")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API错误: {response.status}, {error_text}")
                        return f"错误: {response.status}"
        
        except Exception as e:
            logger.error(f"Ollama生成失败: {e}")
            return f"错误: {str(e)}"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        对话模式
        
        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
        
        Returns:
            助手回复
        """
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("message", {}).get("content", "")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama Chat API错误: {response.status}, {error_text}")
                        return f"错误: {response.status}"
        
        except Exception as e:
            logger.error(f"Ollama对话失败: {e}")
            return f"错误: {str(e)}"
    
    async def embeddings(self, text: str) -> List[float]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本
        
        Returns:
            嵌入向量
        """
        try:
            url = f"{self.base_url}/api/embeddings"
            
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("embedding", [])
                    else:
                        logger.error(f"Ollama Embeddings API错误: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {e}")
            return []
    
    async def check_model(self) -> bool:
        """检查模型是否可用"""
        try:
            url = f"{self.base_url}/api/tags"
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        models = result.get("models", [])
                        model_names = [m.get("name") for m in models]
                        
                        if self.model in model_names:
                            logger.info(f"模型可用: {self.model}")
                            return True
                        else:
                            logger.warning(f"模型不存在: {self.model}, 可用模型: {model_names}")
                            return False
                    else:
                        logger.error(f"无法连接到Ollama服务: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"检查模型失败: {e}")
            return False
