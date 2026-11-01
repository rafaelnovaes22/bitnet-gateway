"""Cerebro via OpenCode headless, na cota gratis do Muse Spark.

PORQUE subprocesso: o free tier do Zen so responde dentro do OpenCode,
a API direta devolve FreeTierError. Este modulo traduz chat em
`opencode run` e devolve texto, sem chave e sem custo.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
import time
from collections.abc import Iterator
from pathlib import Path

MODELO_PADRAO = "opencode/muse-spark-1.3-contributor-free"
LIMITE_S = 600
MAX_MSGS = 10
MAX_CHARS = 4000
INSTRUCAO = "Voce e o cerebro do bot Hermes no Telegram. Responda direto, em PT-BR, sem rodeios."

_TRAVA = threading.Lock()


def _workspace() -> Path:
    pasta = Path.home() / ".hermes" / "workspace"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _binario() -> str:
    caminho = shutil.which("opencode")
    if not caminho:
        raise RuntimeError("binario opencode ausente no PATH, esperado login com cota gratis")
    return caminho


def montar_prompt(mensagens: list[dict]) -> str:
    """Achata o historico OpenAI em texto, com teto antiestouro de cota."""
    blocos: list[str] = []
    for msg in mensagens[-MAX_MSGS:]:
        papel = msg.get("role")
        rotulo = "Usuario" if papel == "user" else "Assistente" if papel == "assistant" else "Sistema"
        conteudo = msg.get("content") or ""
        if isinstance(conteudo, list):
            conteudo = " ".join(p.get("text", "") for p in conteudo if isinstance(p, dict))
        texto = str(conteudo).strip()
        if texto:
            blocos.append(f"{rotulo}: {texto}")
    prompt = "\n\n".join(blocos)
    if len(prompt) > MAX_CHARS:
        prompt = prompt[-MAX_CHARS:]
    return prompt


def extrair_texto(linhas: list[str]) -> str:
    """Pesca deltas de texto dos eventos --format json, um por linha."""
    partes: list[str] = []
    for linha in linhas:
        try:
            evento = json.loads(linha)
        except (json.JSONDecodeError, TypeError, AttributeError):
            continue
        if isinstance(evento, dict) and evento.get("type") == "text":
            texto = ((evento.get("part") or {}).get("text") or "").strip()
            if texto:
                partes.append(texto)
    return "\n".join(partes).strip()


def fluxo(mensagens: list[dict], limite_s: int = LIMITE_S) -> Iterator[str]:
    """Roda o cerebro isolado e entrega deltas ao vivo, uma chamada por vez."""
    prompt = montar_prompt(mensagens)
    if not prompt:
        raise ValueError("prompt vazio apos montar mensagens")
    # A persona do Hermes (14k, ferramentas que nao existem aqui) so
    # atrapalha o Spark e estoura limite do opencode: config enxuta.
    prompt = f"{INSTRUCAO}\n\n{prompt}"
    inicio = time.monotonic()
    with _TRAVA:
        proc = subprocess.Popen(
            [_binario(), "run", "-m", MODELO_PADRAO, "--format", "json"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(_workspace()),
        )
        cacos_erro: list[str] = []
        try:
            assert proc.stdout is not None
            assert proc.stderr is not None
            assert proc.stdin is not None
            import threading as _th

            def _drenar_erro() -> None:
                for linha in proc.stderr:
                    cacos_erro.append(linha)

            _fio = _th.Thread(target=_drenar_erro, daemon=True)
            _fio.start()
            # Prompt via stdin: argv estoura o limite do Windows no prompt do Hermes.
            try:
                proc.stdin.write(prompt)
                proc.stdin.close()
            except BrokenPipeError:
                pass
            for linha in proc.stdout:
                if time.monotonic() - inicio > limite_s:
                    proc.kill()
                    raise TimeoutError(f"cerebro estourou {limite_s}s sem custo, tente mais curto")
                delta = extrair_texto([linha])
                if delta:
                    yield delta
            proc.wait(timeout=30)
            _fio.join(timeout=10)
        finally:
            if proc.poll() is None:
                proc.kill()
        if proc.returncode != 0:
            detalhe = "".join(cacos_erro)[-800:]
            raise RuntimeError(f"opencode falhou rc={proc.returncode}: {detalhe}")


def responder(mensagens: list[dict], limite_s: int = LIMITE_S) -> str:
    """Versao bloqueante do fluxo, para respostas nao streamadas."""
    texto = "".join(fluxo(mensagens, limite_s))
    if not texto:
        raise RuntimeError("cerebro voltou vazio, sem custo e sem resposta")
    return texto
