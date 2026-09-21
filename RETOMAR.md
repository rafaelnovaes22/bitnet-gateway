# RETOMAR, ponto de pausa em 2026-09-21

## Status
MVP BitNet Gateway no ar via tunel gratuito Cloudflare. Pausado para retomar em 2026-09-22.

## URL publica momentanea
https://does-consistent-hardly-respect.trycloudflare.com
- Raiz `/` abre demo humana. `/health` retorna ok (verificado em 2026-09-21).
- Vive enquanto os processos abaixo estiverem vivos nesta maquina.

## Processos vivos na pausa
- python PID 14952 e 20280, inicio 01:12 (uvicorn porta 8123, um pode ser resquicio)
- cloudflared PID 19112, inicio 01:14
- Se amanha a URL falhar: checar `Get-Process python,cloudflared`, matar e relancar com os comandos da secao Voltar.

## Codigo
- Repo: https://github.com/rafaelnovaes22/bitnet-gateway
- Branch de trabalho: `feat/bitnet-gateway-mvp`, `main` como base.
- PR aberta sem merge: https://github.com/rafaelnovaes22/bitnet-gateway/pull/1
- Gates verdes na pausa: `pytest -q` com 7 passed.

## Pendencias
1. Deploy definitivo bloqueado: Railway trial expirado (projeto novo e servico novo, ambos recusados). Requer selecionar plano no workspace Novais Digital.
2. Alternativas gratuitas testadas: HF Spaces Docker e Gradio exigem PRO. Tunel Cloudflare adotado como palco momentaneo.
3. Este arquivo RETOMAR.md ainda nao foi commitado.

## Producao gratis (2026-09-21)

Render Live: https://bitnet-gateway.onrender.com (`/health` ok, `/api/decide` ok, validados em 2026-09-21).
Hermes no Railway com `BITNET_GATEWAY_URL` apontando para essa URL (variavel setada, verificada).
Falta: pinger cron-job.org no `/health` contra o sleep do plano free. Filtro ativa no Hermes quando PR do prefilter mergear e Railway redeployar.

1. Tunel persiste no boot: `manter-no-ar.ps1` relanca uvicorn na 8123 e cloudflared, atalho `bitnet-gateway.cmd` na pasta Startup. URL muda a cada restart (limite do quick tunnel gratis).
2. URL fixa gratis: `render.yaml` (plano free, health `/health`) pronto na branch. Falta conta Render gratis do Rafael, Blueprint do PR 1, pinger cron-job.org no `/health` contra o sleep do plano free.

Revalidado em 2026-09-21: pytest 7 passed, `/health` local e tunel ok (uptime 1056s), branch `feat/bitnet-gateway-mvp` com so `RETOMAR.md` pendente.

## Voltar
```powershell
Set-Location "C:\Users\Rafael\Projetos\bitnet-gateway"
python -m pytest -q
Get-Process python,cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Process python -ArgumentList "-m","uvicorn","app.main:app","--port","8123" -WorkingDirectory "C:\Users\Rafael\Projetos\bitnet-gateway" -WindowStyle Hidden
Start-Process C:\Users\Rafael\AppData\Local\Temp\opencode\cloudflared.exe -ArgumentList "tunnel","--url","http://127.0.0.1:8123","--no-autoupdate" -RedirectStandardOutput $env:TEMP\opencode\tunel.out.log -RedirectStandardError $env:TEMP\opencode\tunel.err.log -WindowStyle Hidden
```
Pegar a nova URL em `tunel.err.log` (padrao `https://...trycloudflare.com`) e validar `/health`.
