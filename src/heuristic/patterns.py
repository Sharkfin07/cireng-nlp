"""Regex patterns for grooming detection."""

import re


PATTERNS = {
    "FRIENDSHIP": [
        r"berapa\s+umur",
        r"a\s*[/\.]\s*s\s*[/\.]\s*l",
    ],
    "RISK_ASSESSMENT": [
        r"orang\s+tua.*ada",
        r"hapus.*chat",
    ],
    "APPROACH": [
        r"ketemu.*kapan",
        r"mau.*jemput",
    ],
}


def matches_pattern(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the given regex patterns."""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
