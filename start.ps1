param(
    [switch]$InitDb
)

Set-Location $PSScriptRoot

Write-Host "=== 医疗大模型测试平台 · 本地启动 ===" -ForegroundColor Green
Write-Host "请确保本地 MySQL/Redis 已在 C:\Programs\Project\docker-compose\database 中运行 (docker compose up -d mysql redis)" -ForegroundColor Cyan

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "未检测到 uv，请参考 https://github.com/astral-sh/uv 安装" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path '.env')) {
    Write-Host "创建 .env 文件..." -ForegroundColor Yellow
    Copy-Item '.env.example' '.env'
    Write-Host "已创建 .env，请按需修改配置" -ForegroundColor Green
}

if (-not (Test-Path '.venv')) {
    Write-Host "创建 Python 3.13 虚拟环境 (.venv)..." -ForegroundColor Yellow
    uv venv --python 3.13
}

Write-Host "同步 Python 依赖..." -ForegroundColor Yellow
uv sync

if ($InitDb) {
    Write-Host "初始化数据库表..." -ForegroundColor Yellow
    uv run python backend/init_db.py
}

Write-Host "启动本地后端服务: http://localhost:8000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可退出" -ForegroundColor Yellow
uv run -- uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
