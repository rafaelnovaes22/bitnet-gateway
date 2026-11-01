from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.spark import extrair_texto, fluxo, montar_prompt, responder


def test_montar_prompt_achata_e_limita() -> None:
    mensagens = [{"role": "system", "content": "s"}] + [
        {"role": "user", "content": f"msg {i}"} for i in range(100)
    ]
    prompt = montar_prompt(mensagens)
    assert "msg 99" in prompt
    assert "msg 0" not in prompt
    assert len(prompt) <= 15000


def test_montar_prompt_lista_openai() -> None:
    mensagens = [{"role": "user", "content": [{"type": "text", "text": "ola"}]}]
    assert "ola" in montar_prompt(mensagens)


def test_extrair_texto_pesca_eventos() -> None:
    linhas = [
        json.dumps({"type": "step_start"}),
        json.dumps({"type": "text", "part": {"text": "ok"}}),
        "lixo nao json",
    ]
    assert extrair_texto(linhas) == "ok"


def _popen_falso():
    falso = MagicMock()
    falso.stdout = iter(
        [
            json.dumps({"type": "text", "part": {"text": "oi"}}) + "\n",
            json.dumps({"type": "text", "part": {"text": "mundo"}}) + "\n",
        ]
    )
    falso.wait.return_value = 0
    falso.poll.return_value = 0
    falso.returncode = 0
    return falso


def test_responder_junta_deltas() -> None:
    with patch("app.spark.subprocess.Popen", return_value=_popen_falso()):
        assert responder([{"role": "user", "content": "oi"}]) == "oimundo"


def test_fluxo_erro_retorno() -> None:
    falso = _popen_falso()
    falso.returncode = 1
    with patch("app.spark.subprocess.Popen", return_value=falso):
        with pytest.raises(RuntimeError):
            list(fluxo([{"role": "user", "content": "oi"}]))
