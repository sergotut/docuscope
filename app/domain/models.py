"""
Модели доменного слоя для сервиса Документоскоп.

Здесь определяются основные бизнес-сущности:
User, Document, Report — используются для представления и
валидации данных на уровне домена.
"""

from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    """
    Модель пользователя системы.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        tg_id (int): Telegram ID пользователя.
    """
    id: int
    tg_id: int


class Document(BaseModel):
    """
    Модель документа (договора), загруженного пользователем.

    Attributes:
        id (int): Уникальный идентификатор документа.
        user_id (int): ID пользователя, загрузившего документ.
        file_hash (str): SHA-256 хэш файла.
        filename (str): Оригинальное имя файла.
        status (str): Текущий статус обработки документа.
        created_at (datetime): Дата и время загрузки документа.
    """
    id: int
    user_id: int
    file_hash: str
    filename: str
    status: str
    created_at: datetime


class Report(BaseModel):
    """
    Модель отчёта по документу.

    Attributes:
        id (int): Уникальный идентификатор отчёта.
        document_id (int): ID связанного документа.
        jsonb_report (dict): Структурированный отчёт по документу (JSONB).
        created_at (datetime): Дата и время создания отчёта.
    """
    id: int
    document_id: int
    jsonb_report: dict
    created_at: datetime
