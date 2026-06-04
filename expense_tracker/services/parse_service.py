from __future__ import annotations

import unicodedata
from datetime import datetime
from typing import Optional

def parse_amount(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None
    raw = str(s).strip().replace("$", "").replace(",", "")
    if raw.startswith("(") and raw.endswith(")"):
        raw = "-" + raw[1:-1]
    try:
        return float(raw)
    except Exception:
        return None

# A simple month key helper: 'YYYY-MM'
def month_key(dt: datetime | str) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m")

    s = dt.strip()
    if len(s) == 7:  # YYYY-MM
        return s

    # YYYY-MM-DD → YYYY-MM; otherwise fall back to current month
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m")
    except ValueError:
        return datetime.now().strftime("%Y-%m")

def month_to_int(s: str) -> Optional[int]:
    if not s:
        return None
    s = unicodedata.normalize("NFKC", s).strip().lower().replace(".", "")
    s = s.replace("ó", "o")
    if s.isdigit():
        n = int(s)
        return n if 1 <= n <= 12 else None
    en = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    en_abbr = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    es = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    es_abbr = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    extra = {"sept": 9, "set": 9}
    if s in extra:
        return extra[s]
    for i, name in enumerate(en, 1):
        if s == name or name.startswith(s):
            return i
    for i, name in enumerate(es, 1):
        if s == name or name.startswith(s):
            return i
    for i, name in enumerate(en_abbr, 1):
        if s == name:
            return i
    for i, name in enumerate(es_abbr, 1):
        if s == name:
            return i
    return None

def _normalize_month_input_to_ym(s: str) -> Optional[str]:
    """
    Strict: accepts ONLY 'YYYY-MM' and returns 'YYYY-MM'.
    """
    s = (s or "").strip()
    if not s:
        return None

    if len(s) != 7 or s[4] != "-":
        return None

    yyyy, mm = s[:4], s[5:]
    if not (yyyy.isdigit() and mm.isdigit()):
        return None

    try:
        datetime.strptime(s, "%Y-%m")
        return s
    except ValueError:
        return None