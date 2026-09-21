"""Log estruturado JSON com campos nomeados."""

from __future__ import annotations

import json
import logging
import time


def configurar() -> logging.Logger:
    logger = logging.getLogger("bitnet-gateway")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(_Formatador())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


class _Formatador(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "nivel": record.levelname.lower(),
                "modulo": record.name,
                "mensagem": record.getMessage(),
            },
            ensure_ascii=False,
        )
