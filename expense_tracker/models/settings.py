from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass, field

from expense_tracker.services.csv_service import _atomic_write_text, _maybe_backup

try:
    from platformdirs import user_config_dir
except ImportError:
    user_config_dir = None

APP_DIR = (
    user_config_dir("ExpenseTracker", "YourOrg") if user_config_dir
    else os.path.join(os.path.expanduser("~"), ".expense_tracker")
)
os.makedirs(APP_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OLD_SETTINGS = os.path.join(BASE_DIR, "settings.json")
if os.path.exists(OLD_SETTINGS) and not os.path.exists(SETTINGS_FILE):
    try:
        shutil.move(OLD_SETTINGS, SETTINGS_FILE)
    except OSError:
        pass

@dataclass
class AppSettings:
    username: str = "Matthew"
    expense_file: str = ""
    lang: str = "en"
    last_qa_cat_key: str = ""
    last_qa_sub_key: str = ""
    annual_budgets: dict[str, dict[str, float]] = field(default_factory=dict)
    income_items: list[dict] = field(default_factory=list)
    # user-editable category taxonomy (seeded from TRANSLATIONS)
    taxonomy: dict = field(default_factory=dict)
    
def _log_err(context: str, err: Exception) -> None:
    """Best-effort stderr logging; never raises."""
    try:
        print(f"[ExpenseTrackerGUI] {context}: {err}", file=sys.stderr)
    except OSError:
        pass

def load_settings() -> AppSettings:
    if not os.path.exists(SETTINGS_FILE):
        return AppSettings()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)

        income_items = raw.get("income_items", [])
        if not isinstance(income_items, list):
            income_items = []

        taxonomy = raw.get("taxonomy", {})
        if not isinstance(taxonomy, dict):
            taxonomy = {}

        return AppSettings(
            username=raw.get("username", "Matthew"),
            expense_file=raw.get("expense_file", ""),
            lang=raw.get("lang", "en"),
            last_qa_cat_key=raw.get("last_qa_cat_key", ""),
            last_qa_sub_key=raw.get("last_qa_sub_key", ""),
            annual_budgets=raw.get("annual_budgets", {}) or {},
            income_items=income_items,
            taxonomy=taxonomy,
        )
    except Exception as e:
        _log_err("Failed to load settings.json; falling back to defaults", e)
        return AppSettings()

def save_settings(s: AppSettings) -> None:
    data = {
        "username": s.username,
        "expense_file": s.expense_file,
        "lang": s.lang,
        "last_qa_cat_key": s.last_qa_cat_key,
        "last_qa_sub_key": s.last_qa_sub_key,
        "annual_budgets": s.annual_budgets,
        "income_items": [
            asdict(x) if hasattr(x, "__dataclass_fields__") else dict(x)
            for x in (s.income_items or [])
        ],
        "taxonomy": s.taxonomy or {},
    }

    _maybe_backup(SETTINGS_FILE)
    _atomic_write_text(SETTINGS_FILE, json.dumps(data, indent=2))