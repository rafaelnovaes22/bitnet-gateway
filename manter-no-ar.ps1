$ErrorActionPreference = 'SilentlyContinue'
$proj = 'C:\Users\Rafael\Projetos\bitnet-gateway'
$logDir = Join-Path $env:TEMP 'opencode'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
Get-Process python,cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Start-Process python -ArgumentList '-m','uvicorn','app.main:app','--port','8123' -WorkingDirectory $proj -WindowStyle Hidden
Start-Process "$env:TEMP\opencode\cloudflared.exe" -ArgumentList 'tunnel','--url','http://127.0.0.1:8123','--no-autoupdate' -RedirectStandardOutput (Join-Path $logDir 'tunel.out.log') -RedirectStandardError (Join-Path $logDir 'tunel.err.log') -WindowStyle Hidden
Start-Sleep 12
Select-String -Path (Join-Path $logDir 'tunel.err.log') -Pattern 'https://.*trycloudflare.com' | Select-Object -Last 1
