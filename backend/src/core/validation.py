"""Input sanitization helpers (XSS / control-char defense).

Message/note content is stored as-is but rendered as text on the frontend (React
escapes by default). For any field that could be rendered as HTML, use
``sanitize_text`` to neutralize markup and strip control characters.
"""

import html
import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def strip_control_chars(value: str) -> str:
    return _CONTROL_CHARS.sub("", value)


def sanitize_text(value: str, *, max_length: int | None = None) -> str:
    """Strip control chars and HTML-escape angle brackets/quotes."""
    cleaned = strip_control_chars(value).strip()
    cleaned = html.escape(cleaned, quote=True)
    if max_length is not None:
        cleaned = cleaned[:max_length]
    return cleaned
