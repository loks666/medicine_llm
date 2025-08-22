from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from backend.app.models import User
from backend.app.schemas import UserLogin, UserResponse
from backend.app.services.crypto import verify_password, hash_password
from backend.app.services.session import create_session, delete_session
from backend.app.services.jwt_auth import create_access_token, get_hardcoded_token
from backend.app.deps import get_current_user

from backend.app.db import get_db

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username
        }
    }

@router.post("/logout")
async def logout():
    """用户登出"""
    # JWT是无状态的，客户端删除token即可
    return {"message": "登出成功"}

@router.get("/hardcoded-token")
async def get_demo_token():
    """获取写死的演示token（仅用于开发测试）"""
    token = get_hardcoded_token()
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "这是一个写死的演示token，用于测试JWT认证"
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

# 创建默认用户的辅助函数（仅用于开发测试）
@router.post("/create-demo-user")
async def create_demo_user(db: Session = Depends(get_db)):
    """创建演示用户（仅开发环境）"""
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.username == "demo").first()
    if existing_user:
        return {"message": "演示用户已存在"}
    
    # 创建演示用户
    demo_user = User(
        username="demo",
        password_hash=hash_password("demo123")
    )
    
    db.add(demo_user)
    db.commit()
    
    return {"message": "演示用户创建成功", "username": "demo", "password": "demo123"}