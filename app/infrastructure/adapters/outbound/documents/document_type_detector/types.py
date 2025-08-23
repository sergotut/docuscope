"""Публичные типы API адаптеров детекторов документов."""

from __future__ import annotations

from typing import Literal, TypeAlias

__all__ = ["DecisionBasis"]

DecisionBasis: TypeAlias = Literal[
    "signature_match",
    "container_hint",
    "extension_only",
    "insufficient_evidence",
]
