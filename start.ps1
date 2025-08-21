# 医疗大模型测试平台启动脚本
# PowerShell版本

Write-Host "=== 医疗大模型测试平台 Docker 启动脚本 ===" -ForegroundColor Green
Write-Host ""

# 检查Docker是否运行
Write-Host "检查Docker状态..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker正在运行" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker未运行，请先启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查是否存在.env文件
if (-not (Test-Path ".env")) {
    Write-Host "创建.env文件..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ 已创建.env文件，请根据需要修改配置" -ForegroundColor Green
}

# 停止现有容器（如果存在）
Write-Host "停止现有容器..." -ForegroundColor Yellow
docker-compose down

# 构建并启动服务
Write-Host "构建并启动服务..." -ForegroundColor Yellow
docker-compose up --build -d

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "检查服务状态..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "=== 服务启动完成 ===" -ForegroundColor Green
Write-Host "前端地址: http://localhost:3001" -ForegroundColor Cyan
Write-Host "后端API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看日志: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "停止服务: docker-compose down" -ForegroundColor Yellow
Write-Host ""