"""Regex patterns for grooming detection."""

import re


PATTERNS = {
    "FRIENDSHIP": [
        r"berapa\s+umur",
        r"a\s*[/\.]\s*s\s*[/\.]\s*l",
        r"foto\s+(kamu|lo|lu)",
        r"nama\s+kamu",
    ],
    "RELATIONSHIP": [
        r"hobby\s+(kamu|lo|lu)",
        r"keluarga.*mana",
        r"orang tua.*apa",
        r"suka.*apa",
    ],
    "RISK_ASSESSMENT": [
        r"orang\s+tua.*ada",
        r"hapus.*chat",
        r"delete.*pesan",
        r"jangan.*kasih.*tahu",
        r"ada\s+yang\s+liat",
        r"lagi\s+sama\s+(siapa|sianu)",
    ],
    "EXCLUSIVITY": [
        r"rahasia\s+(kita|kamu|lo|lu)",
        r"cuma\s+(kita|kamu|lo|lu)\s+berdua",
        r"jangan\s+bilang",
        r"special\s+(buat|untuk)",
        r"gak\s+ada\s+yang\s+ngerti",
    ],
    "SEXUAL": [
        r"open\s+bo",
        r"sex",
        r"porno",
        r"nude",
        r"payudara",
        r"junior",
    ],
    "APPROACH": [
        r"mau.*ketemu",
        r"ketemuan\s+(yuk|dong)",
        r"aku\s+jemput",
        r"rumahnya.*mana",
        r"kapan\s+bisa\s+ketemu",
        r"mau\s+kemana",
        r"pindah.*discord",
        r"pindah.*wa",
        r"pindah.*whatsapp",
    ],
}


def matches_pattern(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the given regex patterns."""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def get_matching_patterns(text: str, patterns: list[str]) -> list[str]:
    """Get all matching patterns from a list."""
    matches = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
    return matches
