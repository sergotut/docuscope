"""Shim: реэкспорт адаптера TiktokenTokenizer из подпакета tiktoken.

Служит для обратной совместимости.
"""

from .tiktoken import TiktokenTokenizer

__all__ = ["TiktokenTokenizer"]
