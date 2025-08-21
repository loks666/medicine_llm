from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# 用户相关
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 会话相关
class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationResponse):
    messages: List['MessageResponse'] = []

# 消息相关
class MessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    model: str
    created_at: datetime
    rating: Optional[int] = None
    rating_comment: Optional[str] = None
    
    class Config:
        from_attributes = True

# 聊天相关
class ChatRequest(BaseModel):
    conv_id: int
    model: str
    prompt: str
    system_prompt: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

# 评价相关
class MessageRating(BaseModel):
    rating: int  # 0=差评, 1=好评
    comment: Optional[str] = None

# SSE事件
class SSEChunk(BaseModel):
    delta: str
    message_id: int

class SSEDone(BaseModel):
    message_id: int
    full: str

# 更新前向引用
ConversationWithMessages.model_rebuild()