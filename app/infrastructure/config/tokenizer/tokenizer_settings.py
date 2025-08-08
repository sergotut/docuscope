"""Секция настроек токенизатора (tiktoken)."""

from pydantic import Field

from ..base import SettingsBase


class TokenizerSettings(SettingsBase):
    """Параметры tiktoken."""

    tokenizer_model: str = Field(
        "gpt2", description="Имя модели для tiktoken.get_encoding()"
    )
