import os
from typing import Optional

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - 安装失败时提示
    Redis = None  # type: ignore

_redis_client: Optional["Redis"] = None


def _build_redis_url() -> str:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "63791")
    password = os.getenv("REDIS_PASSWORD", "jax666")
    db = os.getenv("REDIS_DB", "0")
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"


def get_redis() -> Optional["Redis"]:
    """延迟初始化 Redis 客户端，连接失败时返回 None。"""
    global _redis_client
    if Redis is None:
        return None

    if _redis_client is None:
        url = os.getenv("REDIS_URL") or _build_redis_url()
        try:
            _redis_client = Redis.from_url(url, decode_responses=True)
        except Exception as exc:
            print(f"Redis 初始化失败: {exc}")
            _redis_client = None
    return _redis_client


def reset_redis_client() -> None:
    """测试或异常情况下重置 Redis 客户端。"""
    global _redis_client
    _redis_client = None


async def close_redis() -> None:
    """应用关闭时释放 Redis 连接。"""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.close()
        finally:
            _redis_client = None
