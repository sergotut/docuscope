"""Утилиты клиента Postgres: безопасная маскировка DSN/URL."""

from __future__ import annotations

import re
from typing import Final
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

__all__ = ["mask_dsn"]

# Ключи, которые считаем секретными (и в URL, и в key=value DSN).
_SECRET_KEYS: Final[tuple[str, ...]] = (
    "password",
    "passwd",
    "pwd",
    "sasl_password",
    "saslpassword",
    "token",
    "access_token",
    "secret",
    "secret_key",
    "access_key",
    "api_key",
    "apikey",
)

# Регекс для libpq-строки вида key=value с квотами или без.
# Маскируем только секретные ключи из списка выше.
_KV_RE: Final[re.Pattern[str]] = re.compile(
    rf"""
    (?ix)                                   # ignorecase + verbose
    \b
    (?:{ "|".join(map(re.escape, _SECRET_KEYS)) })   # секретный ключ
    \b
    \s*=\s*
    (                                       # значение:
      '(?:\\.|[^'])*'                       # 1) 'в кавычках' с эскейпом
      |                                     # 2) "в кавычках"
      "(?:\\.|[^"])*"
      |                                     # 3) без кавычек до пробела
      [^\s]+
    )
    """,
)


def _mask_url_like(dsn: str, replacement: str) -> str:
    """Маскирует секреты в URL-подобном DSN.

    Args:
        dsn (str): Строка подключения (postgres://user:pass@host/db?...).
        replacement (str): Строка-маска.

    Returns:
        str: Маскированный DSN.
    """
    parts = urlsplit(dsn)
    netloc = parts.netloc

    # Маскируем userinfo (user:pass@host). Сохраняем хост/порт как есть.
    if "@" in netloc:
        userinfo, hostinfo = netloc.rsplit("@", 1)
        # Возможные варианты userinfo:
        #  - user:pass
        #  - user
        #  - :pass  (redis-style)
        if ":" in userinfo:
            user, _pwd = userinfo.split(":", 1)
            new_userinfo = f"{user}:{replacement}"
        else:
            # пароля нет; отдельный случай ":pass"
            new_userinfo = (
                f":{replacement}"
                if (not userinfo or userinfo.startswith(":"))
                else userinfo
            )

        netloc = f"{new_userinfo}@{hostinfo}"

    # Маскируем секреты в query (?password=..., &token=..., ...).
    if parts.query:
        q = parse_qsl(parts.query, keep_blank_values=True)
        q_masked = [(k, replacement if k.lower() in _SECRET_KEYS else v) for k, v in q]
        query = urlencode(q_masked, doseq=True)
    else:
        query = parts.query

    return urlunsplit((parts.scheme, netloc, parts.path, query, parts.fragment))


def _mask_kv_like(dsn: str, replacement: str) -> str:
    """Маскирует секреты в libpq-формате key=value.

    Сохраняет исходные кавычки и большинство пробелов.

    Args:
        dsn (str): Строка вида 'host=... user=... password=...'.
        replacement (str): Строка-маска.

    Returns:
        str: Маскированная строка.
    """

    def _sub(m: re.Match[str]) -> str:
        full = m.group(0)
        # Находим позицию '=' и заменяем только правую часть.
        idx = full.lower().find("=")
        prefix = full[: idx + 1]
        value = full[idx + 1 :].lstrip()
        if value and value[0] in ("'", '"'):
            quote = value[0]
            return f"{prefix} {quote}{replacement}{quote}"
        return f"{prefix} {replacement}"

    return _KV_RE.sub(_sub, dsn)


def mask_dsn(dsn: str, *, replacement: str = "***") -> str:
    """Маскирует пароли/секреты в DSN для безопасного логирования.

    Поддерживает два формата:
      1) URL-подобный (postgres://user:pass@host:port/db?password=...).
      2) libpq key=value (host=... user=... password=...).

    Args:
        dsn (str): Исходный DSN/URL.
        replacement (str): Строка-маска для значений секретов.

    Returns:
        str: Маскированный DSN. Если формат неизвестен — возвращает replacement.
    """
    s = dsn.strip()
    if not s:
        return replacement
    if "://" in s:
        return _mask_url_like(s, replacement)
    # Простейшая эвристика key=value: наличие '='.
    if "=" in s:
        return _mask_kv_like(s, replacement)
    # Непонятный формат — лучше скрыть полностью.
    return replacement
