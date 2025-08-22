import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

# JWT配置
SECRET_KEY = "your-secret-key-here"  # 生产环境应该从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 写死的测试token（用户ID为1的demo用户）
HARDCODED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJkZW1vIiwiZXhwIjoxNzU2NDczNjQ3fQ.8yOGQJYvQXKvQXKvQXKvQXKvQXKvQXKvQXKvQXKvQXK"

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效"
        )

def create_hardcoded_token() -> str:
    """创建写死的测试token（用于demo用户）"""
    # 为demo用户（ID=1）创建一个长期有效的token
    payload = {
        "sub": "1",  # 用户ID
        "username": "demo",
        "exp": datetime.utcnow() + timedelta(days=365)  # 1年有效期
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_hardcoded_token() -> str:
    """获取写死的测试token"""
    # 返回一个预生成的token，避免每次都重新生成
    return create_hardcoded_token()