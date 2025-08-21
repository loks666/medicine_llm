#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db import init_database, check_database_connection, DATABASE_URL
from app.models import User, Conversation, Message, Session

def main():
    print("开始初始化数据库...")
    print(f"数据库URL: {DATABASE_URL}")
    
    # 检查数据库连接
    if not check_database_connection():
        print("❌ 数据库连接失败，请检查配置和服务状态")
        return False
    
    try:
        # 初始化数据库表
        init_database()
        
        print("✅ 数据库初始化成功！")
        print("\n📊 已创建的表:")
        print("  - users (用户表)")
        print("  - conversations (对话表)")  
        print("  - messages (消息表)")
        print("  - sessions (会话表)")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)