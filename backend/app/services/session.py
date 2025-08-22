import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models import Session as SessionModel, User
from backend.app.db import get_db
import os
from dotenv import load_dotenv

load_dotenv()

SESSION_EXPIRE_DAYS = int(os.getenv("SESSION_EXPIRE_DAYS", "7"))

def create_session(db: Session, user_id: int) -> str:
    """创建用户会话"""
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRE_DAYS)
    
    db_session = SessionModel(
        session_id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(db_session)
    db.commit()
    
    return session_id

def get_user_by_session(db: Session, session_id: str) -> User | None:
    """根据会话ID获取用户"""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.expires_at > datetime.utcnow()
    ).first()
    
    if session:
        return session.user
    return None

def delete_session(db: Session, session_id: str) -> bool:
    """删除会话"""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()
    
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def cleanup_expired_sessions(db: Session):
    """清理过期会话"""
    expired_sessions = db.query(SessionModel).filter(
        SessionModel.expires_at <= datetime.utcnow()
    ).all()
    
    for session in expired_sessions:
        db.delete(session)
    
    db.commit()
    return len(expired_sessions)