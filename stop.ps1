# 医疗大模型测试平台停止脚本
# PowerShell版本

Write-Host "=== 医疗大模型测试平台 Docker 停止脚本 ===" -ForegroundColor Red
Write-Host ""

# 停止并移除容器
Write-Host "停止并移除容器..." -ForegroundColor Yellow
docker-compose down

# 可选：移除镜像（取消注释以启用）
# Write-Host "移除镜像..." -ForegroundColor Yellow
# docker-compose down --rmi all

# 可选：移除数据卷（取消注释以启用，注意：这会删除数据库数据）
# Write-Host "移除数据卷..." -ForegroundColor Yellow
# docker-compose down -v

Write-Host ""
Write-Host "=== 服务已停止 ===" -ForegroundColor Green
Write-Host ""