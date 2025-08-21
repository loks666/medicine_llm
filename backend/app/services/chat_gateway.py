import httpx
import json
import asyncio
from typing import AsyncGenerator, List, Dict, Any
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://your-gateway.example.com")
API_KEY = os.getenv("API_KEY", "key")

class ChatGateway:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.timeout = 60.0
    
    async def stream_chat(self, model: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """流式聊天，将OpenAI风格流转换为统一SSE格式"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"网关请求失败: {error_text.decode()}"
                        )
                    
                    accumulated_content = ""
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        # 处理OpenAI风格的SSE数据
                        if line.startswith("data: "):
                            data_str = line[6:]  # 移除"data: "前缀
                            
                            # 检查是否为结束标记
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                
                                # 提取内容增量
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"]:
                                        delta_content = choice["delta"]["content"]
                                        if delta_content:
                                            accumulated_content += delta_content
                                            # 转换为统一SSE格式
                                            yield f"data: {json.dumps({'delta': delta_content})}\n\n"
                                            
                            except json.JSONDecodeError:
                                # 忽略无法解析的行
                                continue
                    
                    # 发送完成事件
                    yield f"data: {json.dumps({'type': 'done', 'content': accumulated_content})}\n\n"
                    
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="请求超时")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"网络请求错误: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"聊天服务错误: {str(e)}")
    
    async def simple_chat(self, model: str, messages: List[Dict[str, str]]) -> str:
        """非流式聊天（用于测试）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"网关请求失败: {response.text}"
                    )
                
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise HTTPException(status_code=500, detail="响应格式错误")
                    
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="请求超时")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"网络请求错误: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"聊天服务错误: {str(e)}")

# 全局实例
chat_gateway = ChatGateway()