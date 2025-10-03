from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
# 优先使用环境变量中的 DATABASE_URL，默认连到本地 docker-compose 提供的 MySQL
def _build_mysql_url() -> str:
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "33061")
    db_name = os.getenv("DB_NAME", "flyai")
    db_user = os.getenv("DB_USER", "fly_user")
    db_password = os.getenv("DB_PASSWORD", "jax666")
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"

DATABASE_URL = os.getenv("DATABASE_URL") or _build_mysql_url()

engine_options = {"echo": False}

if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    engine_options["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库表"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

def check_database_connection():
    """检查数据库连接"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("数据库连接成功")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False
