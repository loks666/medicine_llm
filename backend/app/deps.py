from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.services.session import get_user_by_session

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """获取当前登录用户"""
    session_id = request.cookies.get("sid")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )
    
    user = get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="会话已过期或无效"
        )
    
    return user

def get_optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """获取当前用户（可选）"""
    session_id = request.cookies.get("sid")
    
    if not session_id:
        return None
    
    return get_user_by_session(db, session_id)