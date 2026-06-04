from __future__ import annotations

import csv
import os
import tempfile
from typing import List

from expense_tracker.i18n.translations import TRANSLATIONS

def ensure_csv_with_headers(path: str, lang: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(TRANSLATIONS[lang]["csv_headers"])

def read_rows(path: str) -> List[List[str]]:
    rows: List[List[str]] = []
    if not path or not os.path.exists(path):
        return rows
    try:
        with open(path, "r", newline="", encoding="utf-8", errors="replace") as f:
            r = csv.reader((line.replace("\x00", "") for line in f))
            headers_by_lang = [
                [h.strip().lower() for h in TRANSLATIONS[l]["csv_headers"][:6]]
                for l in TRANSLATIONS
            ]
            saw_any_data = False
            for row in r:
                if not row:
                    continue
                cells = [(row[i] if i < len(row) else "").strip().lower() for i in range(6)]
                is_header = (not saw_any_data) and any(
                    sum(1 for i in range(len(hdrs)) if cells[i] == hdrs[i]) >= 5
                    for hdrs in headers_by_lang
                )
                if is_header:
                    continue
                fixed = [(row[i] if i < len(row) else "") for i in range(6)]
                rows.append(fixed)
                saw_any_data = True
    except Exception as e:
        _log_err(f"Failed to read CSV: {path}", e)
    return rows

def csv_is_header_only(path: str) -> bool:
    """Return True when the CSV contains only a header row (no data rows)."""
    if not path or not os.path.exists(path):
        return False

    try:
        with open(path, "r", newline="", encoding="utf-8", errors="replace") as f:
            r = csv.reader((line.replace("\x00", "") for line in f))
            # Build normalized headers for all supported languages
            headers_by_lang = [
                [h.strip().lower() for h in TRANSLATIONS[l]["csv_headers"][:6]]
                for l in TRANSLATIONS
            ]

            saw_header = False
            for row in r:
                if not row:
                    continue
                cells = [(row[i] if i < len(row) else "").strip().lower() for i in range(6)]

                # Identify a header row (match at least 5 of 6 header columns)
                is_header = any(
                    sum(1 for i in range(len(hdrs)) if cells[i] == hdrs[i]) >= 5
                    for hdrs in headers_by_lang
                )

                if not saw_header:
                    # First meaningful row must be a header to be "header-only"
                    if not is_header:
                        return False
                    saw_header = True
                    continue

                # If we encounter any non-header, non-empty row after header, it's not header-only
                if any(c.strip() for c in row):
                    return False

            # True only if we saw a header and no data rows
            return saw_header
    except Exception:
        return False

def _sanitize_csv_cell(s) -> str:
    s = "" if s is None else str(s)
    if s and s[0] in ("=", "+", "-", "@"):
        return "'" + s
    return s

def _row6(row: list[str]) -> list[str]:
    return [(row[i] if i < len(row) else "") for i in range(6)]

def write_rows(path: str, lang: str, rows: list[list[str]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    out = [TRANSLATIONS[lang]["csv_headers"]]
    for r in rows:
        safe = _row6(r)

        # CSV injection safety: sanitize user-entered text fields
        # [0]=Amount, [1]=Category key, [2]=Subcategory key, [3]=Description, [4]=Date, [5]=Name
        safe[3] = _sanitize_csv_cell(safe[3])  # description
        safe[5] = _sanitize_csv_cell(safe[5])  # name

        out.append(safe)

    _maybe_backup(path)
    _atomic_write_csv(path, out)

def atomic_write(path: str, write_fn) -> None:
    """Generic atomic write helper.

    write_fn will be called with an open text-mode file object (w, encoding utf-8).
    On success, tmp file is moved into place atomically.
    """
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)

    # mkstemp returns an OS-level fd and name; write via fd to avoid race
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".tmp")
    try:
        # Open the fd as a text file and call the writer
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            write_fn(f)
        os.replace(tmp, path)  # atomic move on most OSes
    finally:
        # If something went wrong before os.replace, ensure tmp is removed
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass

def _atomic_write_text(path: str, text: str) -> None:
    """Keep previous call-site semantics: write text atomically."""
    atomic_write(path, lambda f: f.write(text))


def _atomic_write_csv(path: str, rows: List[List[str]]) -> None:
    """Keep previous call-site semantics: write CSV atomically."""
    def _writer(f):
        w = csv.writer(f)
        w.writerows(rows)
    atomic_write(path, _writer)

def _maybe_backup(path: str) -> None:
    """Keep a single backup copy in csv-backup/<filename>.bak1."""
    src_dir = os.path.dirname(path) or "."
    backup_dir = os.path.join(src_dir, "backup")
    os.makedirs(backup_dir, exist_ok=True)

    if not os.path.exists(path):
        return

    bak_name = f"{os.path.basename(path)}.bak1"
    bak_path = os.path.join(backup_dir, bak_name)

    try:
        with open(path, "rb") as src, open(bak_path, "wb") as dst:
            dst.write(src.read())
    except OSError as e:
        _log_err(f"Backup failed for {path}", e)

def _preflight_writable(path: str) -> bool:
    try:
        d = os.path.dirname(path) or "."
        os.makedirs(d, exist_ok=True)
        fd, test = tempfile.mkstemp(dir=d, prefix=".et_write_test_")
        os.close(fd)
        os.remove(test)
        return True
    except OSError:
        return False