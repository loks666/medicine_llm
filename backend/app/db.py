from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "medicine_llm")
DB_USER = os.getenv("DB_USER", "chatuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "chatpass")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=False)
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
            result = connection.execute(text("SELECT 1"))
            print("数据库连接成功")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False