"""Секция настроек эмбеддеров."""

from ..base import SettingsBase
from .base import EmbeddingBaseSettings
from .bge_large import BGELargeEmbeddingSettings
from .bge_large_ru import BGELargeRuEmbeddingSettings
from .e5_mistral import E5MistralEmbeddingSettings
from .gigachat import SberGigaChatEmbeddingSettings
from .sbert_large_ru import SBERTLargeRuEmbeddingSettings
from .sentence_transformers import STEmbeddingSettings
from .yagpt import YaGPTEmbeddingSettings


class EmbeddingsSettings(SettingsBase):
    """Настройки эмбеддеров."""

    base: EmbeddingBaseSettings = EmbeddingBaseSettings()
    yagpt: YaGPTEmbeddingSettings = YaGPTEmbeddingSettings()
    gigachat: SberGigaChatEmbeddingSettings = SberGigaChatEmbeddingSettings()
    st: STEmbeddingSettings = STEmbeddingSettings()
    sbert_large_ru: SBERTLargeRuEmbeddingSettings = SBERTLargeRuEmbeddingSettings()
    bge_large: BGELargeEmbeddingSettings = BGELargeEmbeddingSettings()
    bge_large_ru: BGELargeRuEmbeddingSettings = BGELargeRuEmbeddingSettings()
    e5_mistral: E5MistralEmbeddingSettings = E5MistralEmbeddingSettings()
