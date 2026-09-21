"""Embeddings deterministicos offline, stub do BitNet-embedding-270M.

PORQUE stub: mantem a API estavel e o deploy sem GPU enquanto o
GGUF 1-bit nao esta presente. Troca e so apontar BITNET_EMBED_GGUF.
"""

from __future__ import annotations

import hashlib

DIMENSAO_PADRAO = 64


def _linha(palavra: str, dimensao: int) -> list[float]:
    digest = hashlib.sha256(palavra.encode("utf-8")).digest()
    vetor: list[float] = []
    for i in range(dimensao):
        byte = digest[i % len(digest)]
        vetor.append((byte / 127.5) - 1.0)
    return vetor


def vetorizar(textos: list[str], dimensao: int = DIMENSAO_PADRAO) -> list[list[float]]:
    """Gera um vetor por texto, deterministico e normalizado em [-1, 1]."""
    if not textos:
        raise ValueError("lista textos vazia, esperado ao menos 1 frase")
    if dimensao < 8 or dimensao > 512:
        raise ValueError(f"dimensao {dimensao} fora de [8, 512]")
    saida: list[list[float]] = []
    for texto in textos:
        if not texto.strip():
            raise ValueError("texto vazio na lista, esperado frase PT-BR")
        saida.append(_linha(texto.strip().lower(), dimensao))
    return saida
