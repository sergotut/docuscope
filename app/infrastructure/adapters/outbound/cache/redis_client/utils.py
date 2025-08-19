"""Утилиты для Redis."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit, quote
from typing import Iterable

__all__ = ["mask_url", "SENSITIVE_QUERY_KEYS"]

# Базовый набор чувствительных ключей в query
SENSITIVE_QUERY_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "pass",
        "pwd",
        "secret",
        "token",
        "apikey",
        "api_key",
        "access_token",
        "auth",
        "client_secret",
        "tls_key",
    }
)


def mask_url(
    url: str,
    *,
    placeholder: str = "***",
    extra_sensitive_keys: Iterable[str] | None = None,
) -> str:
    """Маскирует секреты в Redis URL (userinfo и чувствительные query-ключи).

    Правила:
    - В userinfo пароль заменяется на placeholder, имя пользователя сохраняется.
    - В query маскируются значения ключей из SENSITIVE_QUERY_KEYS и
        extra_sensitive_keys.
    - Если строка не похожа на URL (нет '://') или парсинг не удался —
        возвращается placeholder.
    - Поддерживаются IPv6-хосты (в квадратных скобках) и схемы redis/rediss.
    Args:
        url (str): Исходный URL Redis.
        placeholder (str): Чем заменять секреты.
        extra_sensitive_keys (Iterable[str] | None): Доп. ключи для маскировки.

    Returns:
        str: URL с замаскированными секретами или placeholder при ошибке.
    """
    if "://" not in url:
        return placeholder

    try:
        parts = urlsplit(url)
    except Exception:
        return placeholder

    # userinfo (username:password@)
    username = parts.username  # может быть "", если формат ':pass@'
    password = parts.password
    host = parts.hostname or ""
    port = parts.port

    # Восстановим host:port с поддержкой IPv6 (скобки требуются в netloc)
    is_ipv6 = ":" in host and not host.startswith("[")
    host_for_netloc = f"[{host}]" if is_ipv6 else host
    if port is not None:
        host_for_netloc = f"{host_for_netloc}:{port}"

    netloc = host_for_netloc
    if username is not None:
        # username может быть пустой строкой — сохраняем это поведение
        user_enc = quote(username, safe="") if username != "" else ""
        userinfo = user_enc
        if password is not None:
            userinfo = f"{userinfo}:{placeholder}"
        netloc = f"{userinfo}@{host_for_netloc}"

    # query
    sensitive = {k.lower() for k in SENSITIVE_QUERY_KEYS}
    if extra_sensitive_keys:
        sensitive |= {k.lower() for k in extra_sensitive_keys}

    if parts.query:
        pairs = parse_qsl(parts.query, keep_blank_values=True)
        masked_pairs = [
            (k, placeholder) if (k.lower() in sensitive and v) else (k, v)
            for k, v in pairs
        ]
        query = urlencode(masked_pairs, doseq=True)
    else:
        query = ""

    return urlunsplit((parts.scheme, netloc, parts.path, query, parts.fragment))
