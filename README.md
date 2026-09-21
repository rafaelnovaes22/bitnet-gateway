# BitNet Gateway

Camada barata em CPU (papel do BitNet 1-bit) filtra volume. Cerebro Muse Spark 1.3 decide valor.

Mantem Spark 1.3 no nucleo, correto. BitNet 2B nao substitui raciocinio complexo.

## Rotas

Raiz `/` abre produto humano com demo. `GET /health` e `/api/health` para Railway. `POST /api/triage`, `/api/embed`, `/api/decide`.

## Rodar

```bash
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --port 8000
```

## Railway

Build por Dockerfile, health em `/health`. Troca futura: setar `BITNET_MODEL` e apontar GGUF real em `app/triage.py` e `app/embeddings.py` sem mudar contrato.

## Verificacao

```bash
python -m pytest -q
```

Gate atual: 7 passed. Branch `feat/bitnet-gateway-mvp` aguarda revisao, sem merge.

## Economia

Filtro local resolve cerca de 60% a 70% do volume (spam, suporte simples, outro). Spark entra so em venda, urgencia, dinheiro ou confianca abaixo de 0.65. Resultado: menos tokens caros, mesma qualidade no fechamento.
