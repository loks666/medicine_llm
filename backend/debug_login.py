#!/usr/bin/env python3
"""
前端登录问题诊断脚本
"""
import requests
import json

def test_cors_and_auth():
    print("🔍 开始诊断前端登录问题...")
    
    base_url = "http://localhost:8000"
    
    # 测试CORS预检请求
    print("\n1. 测试CORS预检请求...")
    try:
        response = requests.options(
            f"{base_url}/auth/login",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print(f"   CORS预检状态: {response.status_code}")
        print(f"   允许源: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        print(f"   允许凭据: {response.headers.get('Access-Control-Allow-Credentials', '未设置')}")
    except Exception as e:
        print(f"   ❌ CORS预检失败: {e}")
    
    # 测试登录
    print("\n2. 测试登录API...")
    session = requests.Session()
    try:
        login_response = session.post(
            f"{base_url}/auth/login",
            json={"username": "demo", "password": "demo123"},
            headers={
                "Origin": "http://localhost:3001",
                "Content-Type": "application/json"
            }
        )
        print(f"   登录状态: {login_response.status_code}")
        print(f"   响应: {login_response.text}")
        print(f"   Cookies: {login_response.cookies}")
        
        if login_response.status_code == 200:
            # 测试认证检查
            print("\n3. 测试认证检查...")
            me_response = session.get(
                f"{base_url}/auth/me",
                headers={"Origin": "http://localhost:3001"}
            )
            print(f"   认证检查状态: {me_response.status_code}")
            print(f"   响应: {me_response.text}")
        
    except Exception as e:
        print(f"   ❌ 登录测试失败: {e}")
    
    print("\n✅ 诊断完成")

if __name__ == "__main__":
    test_cors_and_auth()