from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 瑙ｅ喅鐩稿瀵煎叆闂
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 瀵煎叆璺敱
from app.routers import auth, conversations, chat, messages
from app.db import init_database, check_database_connection, get_db
from app.services.session import cleanup_expired_sessions
from app.cache import get_redis, close_redis

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

    # 检查 Redis（可选）
    redis_client = get_redis()
    if redis_client is not None:
        try:
            await redis_client.ping()
            print("Redis 连接成功")
        except Exception as exc:
            print(f"Redis 连接失败: {exc}")
    else:
        print("未启用 Redis，继续运行")

    # 清理过期会话
    try:
        db = next(get_db())
        expired_count = cleanup_expired_sessions(db)
        if expired_count > 0:
            print(f"清理了{expired_count} 个过期会话")
    except Exception as e:
        print(f"清理过期会话失败: {e}")

    print("AI模型测试台启动成功！")

    try:
        yield
    finally:
        print("AI模型测试台正在关闭...")
        await close_redis()

app = FastAPI(
    title="AI妯″瀷娴嬭瘯鍙?,
    description="涓€涓敤浜庢祴璇曞ぇ妯″瀷鐨刉eb搴旂敤",
    version="1.0.0",
    lifespan=lifespan
)

# CORS涓棿浠?
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 浠绘剰 Origin
    allow_credentials=False,      # 涓嶈兘甯?Cookie/Authorization
    allow_methods=["*"],
    allow_headers=["*"],
)

# 鍏ㄥ眬寮傚父澶勭悊
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"鏈嶅姟鍣ㄥ唴閮ㄩ敊璇? {str(exc)}"}
    )

# 娉ㄥ唽璺敱锛堝墠绔凡閫氳繃baseURL娣诲姞/api鍓嶇紑锛?
app.include_router(auth.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(messages.router, prefix="/api")

# 鏍硅矾寰?
@app.get("/")
async def root():
    return {
        "message": "AI妯″瀷娴嬭瘯鍙?API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 鍋ュ悍妫€鏌?
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





