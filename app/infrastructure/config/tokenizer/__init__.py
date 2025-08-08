"""Секция настроек tokenizer"""

from ..base import SettingsBase
from .tokenizer_settings import TokenizerSettings


class TokenizerSettings(TokenizerSettings):
    """Настройки tokenizer"""

    base: TokenizerSettings = TokenizerSettings()
