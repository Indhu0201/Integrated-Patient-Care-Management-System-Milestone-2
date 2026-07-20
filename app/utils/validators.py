"""Lightweight validators used across forms."""

from __future__ import annotations

import re
from datetime import datetime

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
_PHONE_RE = re.compile(r"^[+]?[0-9\s\-()]{7,20}$")


def is_email(value: str) -> bool:
    return bool(_EMAIL_RE.match((value or "").strip()))


def is_phone(value: str) -> bool:
    return bool(_PHONE_RE.match((value or "").strip()))


def is_date(value: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime((value or "").strip(), fmt)
        return True
    except ValueError:
        return False


def require(value: str) -> bool:
    return bool((value or "").strip())
