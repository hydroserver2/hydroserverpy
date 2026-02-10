from __future__ import annotations

import re
from typing import Any, Iterable, Mapping, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


_SENSITIVE_KEY_RE = re.compile(
    r"(?:"
    r"pass(word)?|passwd|secret|token|api[_-]?key|apikey|auth|bearer|signature|sig|"
    r"access[_-]?token|refresh[_-]?token|client[_-]?secret"
    r")",
    re.IGNORECASE,
)


def is_sensitive_key(key: Optional[str]) -> bool:
    if not key:
        return False
    return bool(_SENSITIVE_KEY_RE.search(key))


def redact_value(key: str, value: Any) -> Any:
    if is_sensitive_key(key):
        return "REDACTED"
    if isinstance(value, str) and len(value) > 256:
        return value[:256] + "...(truncated)"
    return value


def redact_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    return {k: redact_value(k, v) for k, v in values.items()}


def redact_url(url: str) -> str:
    """
    Redact common secret-bearing URL parts (userinfo and sensitive query params).
    """
    try:
        parts = urlsplit(url)
    except Exception:
        return url

    netloc = parts.netloc
    if "@" in netloc:
        netloc = "<redacted>@" + netloc.split("@", 1)[1]

    query_pairs = []
    for k, v in parse_qsl(parts.query, keep_blank_values=True):
        query_pairs.append((k, "REDACTED" if is_sensitive_key(k) else v))
    redacted_query = urlencode(query_pairs, doseq=True)

    return urlunsplit(
        (parts.scheme, netloc, parts.path, redacted_query, parts.fragment)
    )


def summarize_list(values: Iterable[Any], *, max_items: int = 20) -> str:
    items = list(values)
    if len(items) <= max_items:
        return repr(items)
    return (
        repr(items[:max_items])[:-1] + f", ... (+{len(items) - max_items} more)]"
    )
