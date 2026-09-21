from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_raiz_serve_produto() -> None:
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "BitNet Gateway" in resposta.text


def test_saude_ok() -> None:
    for rota in ("/health", "/api/health"):
        resposta = cliente.get(rota)
        assert resposta.status_code == 200
        assert resposta.json()["status"] == "ok"


def test_decide_contrato() -> None:
    resposta = cliente.post("/api/decide", json={"texto": "Meu boleto veio errado, ajuda?"})
    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["escalar_para_spark"] is True
    assert corpo["cerebro"] == "muse-spark-1.3"


def test_embed_dimensao() -> None:
    resposta = cliente.post("/api/embed", json={"textos": ["ola", "mundo"]})
    corpo = resposta.json()
    assert corpo["dim"] == 64
    assert len(corpo["vetores"]) == 2
