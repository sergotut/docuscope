"""Доменный слой приложения.

Содержит модели, порты, исключения и Shared Kernel — ядро бизнес-логики,
независимое от внешних технологий.
"""

from . import model as model
from . import ports as ports
from . import shared as shared

__all__ = ["model", "ports", "shared"]
