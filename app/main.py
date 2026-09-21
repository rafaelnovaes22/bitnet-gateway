"""Gateway hibrido: BitNet CPU filtra, Muse Spark 1.3 decide."""

from __future__ import annotations

import os
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from .cerebro import montar_resposta
from .embeddings import vetorizar
from .log_json import configurar
from .triage import classificar

INICIO = time.time()
LOG = configurar()
MODO_MODELO = os.getenv("BITNET_MODEL", "bitnet-b1.58-2b-cpu")

app = FastAPI(title="BitNet Gateway")


class EntradaTexto(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)


class EntradaVetores(BaseModel):
    textos: list[str] = Field(min_length=1, max_length=32)


PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BitNet Gateway</title>
<style>body{font-family:system-ui;margin:0;background:#0b0e14;color:#e8ecf3}
.wrap{max-width:720px;margin:0 auto;padding:32px 20px}
.card{background:#141a26;border:1px solid #263048;border-radius:14px;padding:20px;margin-top:16px}
textarea{width:100%;min-height:90px;border-radius:10px;padding:12px;background:#0b0e14;color:#fff;border:1px solid #263048}
button{background:#4f7cff;border:0;color:#fff;padding:12px 18px;border-radius:10px;cursor:pointer;margin-top:12px}
pre{background:#0b0e14;padding:12px;border-radius:10px;overflow:auto}
small{color:#9aa7c2}</style></head><body><div class="wrap">
<h1>BitNet Gateway</h1>
<p>Camada barata em CPU filtra o volume. Muse Spark 1.3 decide o que tem valor.</p>
<div class="card"><textarea id="t">Qual o preco do plano anual?</textarea>
<button onclick="decidir()">Classificar</button><pre id="r">aguardando...</pre>
<small>POST /api/decide, GET /health</small></div>
<script>async function decidir(){const texto=document.getElementById('t').value;
const r=document.getElementById('r');r.textContent='processando...';
const resp=await fetch('/api/decide',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({texto})});r.textContent=JSON.stringify(await resp.json(),null,2);}</script>
</div></body></html>"""


@app.get("/", response_class=HTMLResponse)
def raiz() -> str:
    return PAGINA


def _saude() -> dict[str, object]:
    return {
        "status": "ok",
        "modelo": MODO_MODELO,
        "cerebro": "muse-spark-1.3",
        "uptime_s": int(time.time() - INICIO),
    }


@app.get("/health")
def saude() -> JSONResponse:
    return JSONResponse(_saude())


@app.get("/api/health")
def saude_api() -> JSONResponse:
    return JSONResponse(_saude())


@app.post("/api/triage")
def triagem(entrada: EntradaTexto) -> JSONResponse:
    categoria, confianca = classificar(entrada.texto)
    LOG.info(f"triage categoria={categoria} confianca={confianca:.2f}")
    return JSONResponse({"categoria": categoria, "confianca": round(confianca, 3)})


@app.post("/api/embed")
def incorporar(entrada: EntradaVetores) -> JSONResponse:
    vetores = vetorizar(entrada.textos)
    LOG.info(f"embed n={len(vetores)} dim={len(vetores[0])}")
    return JSONResponse({"dim": len(vetores[0]), "vetores": vetores})


@app.post("/api/decide")
def decidir(entrada: EntradaTexto) -> JSONResponse:
    categoria, confianca = classificar(entrada.texto)
    resposta = montar_resposta(entrada.texto, categoria, confianca)
    LOG.info(f"decide {resposta['cerebro']} {resposta['categoria']}")
    return JSONResponse(resposta)
