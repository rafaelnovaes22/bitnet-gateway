"""Decisao de escalonamento para o cerebro (Muse Spark 1.3).

PORQUE regras explicitas: custo fica previsivel. BitNet filtra,
Spark so entra em dinheiro, urgencia ou baixa confianca.
"""

from __future__ import annotations

TERMOS_DINHEIRO = ("pagamento", "boleto", "pix", "reembolso", "contrato", "fatura")


def precisa_spark(categoria: str, confianca: float, texto: str) -> tuple[bool, str]:
    """Retorna (escalar, motivo) para o cerebro caro."""
    minusculo = texto.lower()
    if categoria in ("urgente", "venda"):
        return (True, f"categoria {categoria} exige resposta do cerebro")
    if confianca < 0.65:
        return (True, f"confianca {confianca:.2f} abaixo do piso 0.65")
    if any(t in minusculo for t in TERMOS_DINHEIRO):
        return (True, "tema com dinheiro exige cerebro com contexto")
    return (False, "camada barata resolve sem cerebro")


def montar_resposta(texto: str, categoria: str, confianca: float) -> dict[str, object]:
    """Monta o envelope de decisao usado pela API e pelos bots."""
    escalar, motivo = precisa_spark(categoria, confianca, texto)
    return {
        "categoria": categoria,
        "confianca": round(confianca, 3),
        "escalar_para_spark": escalar,
        "motivo": motivo,
        "cerebro": "muse-spark-1.3" if escalar else "bitnet-cpu",
    }
