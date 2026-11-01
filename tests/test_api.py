from __future__ import annotations

from unittest.mock import patch

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


def test_chat_completions_compativel() -> None:
    resposta = cliente.post(
        "/v1/chat/completions",
        json={"model": "bitnet-b1.58-2b-cpu", "messages": [{"role": "user", "content": "oi"}]},
    )
    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["object"] == "chat.completion"
    assert corpo["choices"][0]["message"]["role"] == "assistant"
    assert "bitnet-cpu" in corpo["choices"][0]["message"]["content"]


def test_chat_sem_usuario_400() -> None:
    resposta = cliente.post(
        "/v1/chat/completions",
        json={"model": "bitnet-b1.58-2b-cpu", "messages": [{"role": "system", "content": "x"}]},
    )
    assert resposta.status_code == 400


def test_chat_spark_usa_cerebro() -> None:
    with patch("app.main.responder_spark", return_value="ok do spark") as mock:
        resposta = cliente.post(
            "/v1/chat/completions",
            json={"model": "spark-local", "messages": [{"role": "user", "content": "oi"}]},
        )
    assert resposta.status_code == 200
    assert resposta.json()["choices"][0]["message"]["content"] == "ok do spark"
    mock.assert_called_once()


def test_chat_spark_falha_502() -> None:
    with patch("app.main.responder_spark", side_effect=RuntimeError("cota esgotada")):
        resposta = cliente.post(
            "/v1/chat/completions",
            json={"model": "spark-local", "messages": [{"role": "user", "content": "oi"}]},
        )
    assert resposta.status_code == 502
