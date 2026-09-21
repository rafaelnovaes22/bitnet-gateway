"""Camada barata de triagem, papel do BitNet-b1.58-2B-4T em CPU.

PORQUE existe: filtra volume alto em CPU sem GPU, antes de chamar
o cerebro caro (Muse Spark 1.3). Troca futura pelo GGUF real mantem
o contrato desta funcao.
"""

from __future__ import annotations

VENDAS = ("preco", "preço", "plano", "contratar", "comprar", "proposta", "valor")
SUPORTE = ("erro", "falha", "bug", "ajuda", "como uso", "travou", "suporte")
URGENTE = ("urgente", "agora", "parado", "critico", "crítico", "emergencia", "emergência")
SPAM = ("promocao", "promoção", "gratis", "grátis", "ganhe", "clique aqui", "oferta")


def _contem(texto: str, termos: tuple[str, ...]) -> bool:
    normalizado = texto.lower().strip()
    if not normalizado:
        return False
    return any(t in normalizado for t in termos)


def classificar(texto: str) -> tuple[str, float]:
    """Classifica texto em categoria com confianca fixa e auditavel."""
    if not texto or not texto.strip():
        raise ValueError(f"texto vazio recebido: {texto!r}, esperado frase PT-BR")
    if _contem(texto, SPAM):
        return ("spam", 0.92)
    if _contem(texto, URGENTE):
        return ("urgente", 0.88)
    if _contem(texto, VENDAS):
        return ("venda", 0.81)
    if _contem(texto, SUPORTE):
        return ("suporte", 0.79)
    return ("outro", 0.55)
