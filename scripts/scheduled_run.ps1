# Beijing News Pipeline - 定时任务包装脚本
# 由 Windows Task Scheduler 调用

$ProjectRoot = "C:\Users\admin\Desktop\beijing-news-pipeline"
$VenvPython = "$ProjectRoot\.local\airflow-venv\Scripts\python.exe"

$env:AIRFLOW_HOME = "$ProjectRoot\.local\airflow"
$env:MINIO_ACCESS_KEY = "minioadmin"
$env:MINIO_SECRET_KEY = "minioadmin123"
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/airflow"
$env:PYTHONUTF8 = "1"

$logFile = "$ProjectRoot\logs\pipeline-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null

try {
    & $VenvPython "$ProjectRoot\scripts\run_pipeline.py" 2>&1 | Out-File -FilePath $logFile -Encoding UTF8
    $exitCode = $LASTEXITCODE
    $msg = if ($exitCode -eq 0) { "SUCCESS" } else { "FAILED (exit $exitCode)" }
    Add-Content -Path $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Pipeline $msg"
    Write-Output $msg
    exit $exitCode
} catch {
    Add-Content -Path $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $_"
    Write-Output "ERROR: $_"
    exit 1
}
