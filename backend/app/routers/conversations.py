from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models import User, Conversation, Message
from ..schemas import ConversationCreate, ConversationResponse, ConversationWithMessages
from ..deps import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["会话管理"])

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conv_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新会话"""
    conversation = Conversation(
        user_id=current_user.id,
        title=conv_data.title
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的会话列表（最近50个）"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).limit(50).all()
    
    return conversations

@router.get("/{conv_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会话详情及消息"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 获取消息
    messages = db.query(Message).filter(
        Message.conv_id == conv_id
    ).order_by(Message.created_at.asc()).all()
    
    # 手动构建响应
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": messages
    }

@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除会话"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "会话删除成功"}