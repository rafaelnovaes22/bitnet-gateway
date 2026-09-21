from __future__ import annotations

import pytest

from app.cerebro import montar_resposta
from app.triage import classificar


def test_venda_escala_para_spark() -> None:
    categoria, confianca = classificar("Qual o preco do plano anual?")
    resposta = montar_resposta("Qual o preco do plano anual?", categoria, confianca)
    assert categoria == "venda"
    assert resposta["escalar_para_spark"] is True
    assert resposta["cerebro"] == "muse-spark-1.3"


def test_spam_nao_escala() -> None:
    categoria, confianca = classificar("Promocao gratis clique aqui")
    resposta = montar_resposta("Promocao gratis clique aqui", categoria, confianca)
    assert categoria == "spam"
    assert resposta["escalar_para_spark"] is False


def test_texto_vazio_rejeita() -> None:
    with pytest.raises(ValueError):
        classificar("   ")
