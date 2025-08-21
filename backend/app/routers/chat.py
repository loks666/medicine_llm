from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import asyncio
from app.db import get_db
from app.models import User, Conversation, Message, MessageRole
from app.schemas import ChatRequest, ChatMessage
from app.deps import get_current_user
from app.services.chat_gateway import chat_gateway

router = APIRouter(prefix="/chat", tags=["聊天"])

# 简单的防刷机制
user_last_request = {}
REQUEST_INTERVAL = 2  # 2秒间隔

@router.get("/models")
async def get_models():
    """获取可用模型列表"""
    return ["gemini-1.5-pro", "qwen3-235b-a22b", "deepseek-r1", "llama-3.1-405b", "kimi-k2-0711-preview"]

@router.post("/stream")
async def stream_chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """SSE流式聊天"""
    import time
    
    # 简单防刷
    current_time = time.time()
    if current_user.id in user_last_request:
        if current_time - user_last_request[current_user.id] < REQUEST_INTERVAL:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
    user_last_request[current_user.id] = current_time
    
    # 验证会话权限
    conversation = db.query(Conversation).filter(
        Conversation.id == chat_request.conv_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 构建消息列表
    messages = []
    
    # 添加系统提示词（如果有）
    if chat_request.system_prompt:
        messages.append({
            "role": "system",
            "content": chat_request.system_prompt
        })
    
    # 获取历史消息
    history_messages = db.query(Message).filter(
        Message.conv_id == chat_request.conv_id
    ).order_by(Message.created_at.asc()).all()
    
    for msg in history_messages:
        messages.append({
            "role": msg.role.value,
            "content": msg.content
        })
    
    # 添加当前用户消息
    messages.append({
        "role": "user",
        "content": chat_request.prompt
    })
    
    # 保存用户消息到数据库
    user_message = Message(
        conv_id=chat_request.conv_id,
        role=MessageRole.USER,
        content=chat_request.prompt,
        model=chat_request.model
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # 创建助手消息记录（先创建空的，后续更新内容）
    assistant_message = Message(
        conv_id=chat_request.conv_id,
        role=MessageRole.ASSISTANT,
        content="",
        model=chat_request.model
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    async def generate_stream():
        accumulated_content = ""
        
        try:
            async for chunk in chat_gateway.stream_chat(chat_request.model, messages):
                # 解析chunk数据
                if chunk.startswith("data: "):
                    data_str = chunk[6:].strip()
                    try:
                        data = json.loads(data_str)
                        
                        if data.get("type") == "done":
                            # 更新数据库中的完整内容
                            assistant_message.content = data.get("content", accumulated_content)
                            db.commit()
                            
                            # 发送完成事件
                            yield f"event: done\ndata: {{\"message_id\": {assistant_message.id}, \"full\": \"{data.get('content', accumulated_content)}\"}}\n\n"
                            break
                        elif "delta" in data:
                            delta = data["delta"]
                            accumulated_content += delta
                            
                            # 发送增量事件
                            yield f"event: chunk\ndata: {{\"delta\": \"{delta}\", \"message_id\": {assistant_message.id}}}\n\n"
                    
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            # 发送错误事件
            yield f"event: error\ndata: {{\"error\": \"聊天服务错误: {str(e)}\"}}\n\n"
            
            # 删除未完成的助手消息
            db.delete(assistant_message)
            db.commit()
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )