# Beijing News Pipeline - 本地开发启动脚本
# 在 PowerShell 中运行此脚本启动所有服务

$ProjectRoot = $PSScriptRoot
$MinIOExe = Join-Path $ProjectRoot '.local\minio.exe'
$MinIOData = Join-Path $ProjectRoot '.local\minio\data'
$VenvPython = Join-Path $ProjectRoot '.local\airflow-venv\Scripts\python.exe'
$env:AIRFLOW_HOME = Join-Path $ProjectRoot '.local\airflow'
$env:PYTHONUTF8 = '1'  # 解决中文 Windows GBK 编码问题

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Beijing News Pipeline - 启动" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# ─── 1. 检查 PostgreSQL ───────────────────────────
$pgService = Get-Service -Name postgresql* -ErrorAction SilentlyContinue
if (-not $pgService -or $pgService.Status -ne 'Running') {
    Write-Host "[!] PostgreSQL 未运行" -ForegroundColor Yellow
    Write-Host "    请以管理员身份运行: Start-Service postgresql-x64-17" -ForegroundColor Yellow
} else {
    Write-Host "[OK] PostgreSQL 服务运行中" -ForegroundColor Green
}

# ─── 2. 启动 MinIO ───────────────────────────────
$minioProc = Get-Process -Name minio -ErrorAction SilentlyContinue
if (-not $minioProc) {
    Write-Host "[..] 启动 MinIO..." -NoNewline
    Start-Process -FilePath $MinIOExe -ArgumentList "server",$MinIOData,"--console-address",":9001" -WindowStyle Hidden
    Start-Sleep -Seconds 2
    if (Get-Process -Name minio -ErrorAction SilentlyContinue) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " 失败" -ForegroundColor Red
    }
} else {
    Write-Host "[OK] MinIO 已在运行 (PID $($minioProc.Id))" -ForegroundColor Green
}
Write-Host "     API:    http://localhost:9000" -ForegroundColor DarkGray
Write-Host "     Console: http://localhost:9001 (minioadmin / minioadmin123)" -ForegroundColor DarkGray

# ─── 3. 启动 Airflow Webserver ────────────────────
Write-Host "[..] 启动 Airflow webserver (http://localhost:8080)..."
$wsJob = Start-Job -ScriptBlock {
    param($p, $home)
    $env:AIRFLOW_HOME = $home
    $env:PYTHONUTF8 = '1'
    & $p -m airflow webserver -p 8080 2>&1 | Out-Null
} -ArgumentList $VenvPython, $env:AIRFLOW_HOME
Start-Sleep -Seconds 3

# ─── 4. 启动 Airflow Scheduler ────────────────────
Write-Host "[..] 启动 Airflow scheduler..."
$schJob = Start-Job -ScriptBlock {
    param($p, $home)
    $env:AIRFLOW_HOME = $home
    $env:PYTHONUTF8 = '1'
    & $p -m airflow scheduler 2>&1 | Out-Null
} -ArgumentList $VenvPython, $env:AIRFLOW_HOME

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  所有服务已启动！按任意键停止..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL : localhost:5432 (postgres/postgres)" -ForegroundColor DarkGreen
Write-Host "  MinIO      : http://localhost:9000" -ForegroundColor DarkGreen
Write-Host "  MinIO Web  : http://localhost:9001" -ForegroundColor DarkGreen
Write-Host "  Airflow    : http://localhost:8080 (admin / admin)" -ForegroundColor DarkGreen
Write-Host "  新闻 API   : http://localhost:8000/docs (需手动启动)" -ForegroundColor DarkGray
Write-Host "=====================================" -ForegroundColor Cyan

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 清理
Write-Host "[..] 停止服务..."
$wsJob | Stop-Job 2>$null | Remove-Job 2>$null
$schJob | Stop-Job 2>$null | Remove-Job 2>$null
Get-Process -Name minio -ErrorAction SilentlyContinue | Stop-Process -Force 2>$null
Write-Host "[OK] 已停止所有服务" -ForegroundColor Green