Write-Host "=== 医疗大模型测试平台 · 停止本地服务 ===" -ForegroundColor Green

$processes = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine -match 'uvicorn\s+backend\.main:app'
}

if (-not $processes) {
    Write-Host "未检测到正在运行的本地后端服务" -ForegroundColor Yellow
    return
}

foreach ($proc in $processes) {
    try {
        Write-Host "停止进程 PID=$($proc.ProcessId)" -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force
    } catch {
        Write-Host "停止进程失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "本地后端服务已停止" -ForegroundColor Green
