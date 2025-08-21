from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Message, Conversation
from app.schemas import MessageRating
from app.deps import get_current_user

router = APIRouter(prefix="/messages", tags=["消息管理"])

@router.post("/{message_id}/rate")
async def rate_message(
    message_id: int,
    rating_data: MessageRating,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """对消息进行评价"""
    # 查找消息并验证权限
    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或无权限访问"
        )
    
    # 只能评价助手消息
    if message.role.value != "assistant":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能评价助手消息"
        )
    
    # 验证评价值
    if rating_data.rating not in [0, 1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="评价值必须为0（差评）或1（好评）"
        )
    
    # 更新评价
    message.rating = rating_data.rating
    message.rating_comment = rating_data.comment
    
    db.commit()
    
    return {
        "message": "评价成功",
        "message_id": message_id,
        "rating": rating_data.rating,
        "comment": rating_data.comment
    }

@router.get("/{message_id}")
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取消息详情"""
    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或无权限访问"
        )
    
    return {
        "id": message.id,
        "role": message.role.value,
        "content": message.content,
        "model": message.model,
        "created_at": message.created_at,
        "rating": message.rating,
        "rating_comment": message.rating_comment
    }