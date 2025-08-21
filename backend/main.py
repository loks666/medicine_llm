from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 解决相对导入问题
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 导入路由
from app.routers import auth, conversations, chat, messages
from app.db import init_database, check_database_connection
from app.services.session import cleanup_expired_sessions
from app.db import get_db

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在启动AI模型测试台...")
    
    # 检查数据库连接
    if not check_database_connection():
        print("数据库连接失败，请检查配置")
        exit(1)
    
    # 初始化数据库表
    init_database()
    
    # 清理过期会话
    try:
        db = next(get_db())
        expired_count = cleanup_expired_sessions(db)
        if expired_count > 0:
            print(f"清理了 {expired_count} 个过期会话")
    except Exception as e:
        print(f"清理过期会话失败: {e}")
    
    print("AI模型测试台启动成功！")
    
    yield
    
    # 关闭时执行
    print("AI模型测试台正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title="AI模型测试台",
    description="一个用于测试大模型的Web应用",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:3001", "http://127.0.0.1:3001", 
        "http://localhost:3002", "http://127.0.0.1:3002",
        "http://localhost:3003", "http://127.0.0.1:3003",
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:5173", "http://127.0.0.1:5173",  # Vite默认端口
        "null"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

# 注册路由（添加/api前缀）
app.include_router(auth.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(messages.router, prefix="/api")

# 根路径
@app.get("/")
async def root():
    return {
        "message": "AI模型测试台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if check_database_connection() else "disconnected"
    }

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )