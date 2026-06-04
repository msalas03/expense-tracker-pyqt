from expense_tracker_gui import MainWindow
from expense_tracker.services.csv_service import read_rows

import csv

from expense_tracker_gui import (
    ensure_csv_with_headers,
    read_rows,
    write_rows,
    csv_is_header_only,
)
from expense_tracker.i18n.translations import TRANSLATIONS

from datetime import datetime

from expense_tracker.services.parse_service import (
    month_key,
    month_to_int,
    _normalize_month_input_to_ym,
)

from expense_tracker.services.parse_service import parse_amount



def test_open_csv_loads_rows(qtbot, tmp_path):
    csv_path = tmp_path / "expenses.csv"
    csv_path.write_text(
        "Amount,Category,Subcategory,Description,Date,Name\n"
        "12.34,food,groceries,Milk,2026-01-10,Matthew\n",
        encoding="utf-8",
    )

    win = MainWindow()
    qtbot.addWidget(win)

    win._open_path(str(csv_path))

    assert len(win.model.rows) == 1
    assert win.model.rows[0][0] == "12.34"
    assert win.model.rows[0][1] == "food"


def test_save_model_persists_rows(qtbot, tmp_path):
    csv_path = tmp_path / "expenses.csv"

    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.expense_file = str(csv_path)
    win.model.rows = [
        ["50", "food", "groceries", "Test Save", "2026-01-15", "Matthew"]
    ]

    win._save_model()

    rows = read_rows(str(csv_path))
    assert rows == win.model.rows


def test_quick_add_success_writes_to_csv(qtbot, tmp_path, monkeypatch):
    csv_path = tmp_path / "expenses.csv"

    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.expense_file = str(csv_path)

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.information",
        lambda *args, **kwargs: None,
    )

    food_idx = win.qa_cat.findData("food")
    assert food_idx >= 0
    win.qa_cat.setCurrentIndex(food_idx)

    # Refresh subcategories after category selection
    from expense_tracker.gui.tabs.browse_tab import refresh_qa_subs
    refresh_qa_subs(win)

    groceries_idx = win.qa_sub.findData("groceries")
    assert groceries_idx >= 0
    win.qa_sub.setCurrentIndex(groceries_idx)

    win.qa_amount.setText("22.50")
    win.qa_desc.setText("Quick Add Test")
    win.qa_name.setText("Matthew")

    win._quick_add()

    rows = read_rows(str(csv_path))
    assert len(rows) == 1
    assert rows[0][0] == "22.5"
    assert rows[0][1] == "food"
    assert rows[0][2] == "groceries"
    assert rows[0][3] == "Quick Add Test"
    assert rows[0][5] == "Matthew"

def test_ensure_csv_with_headers_creates_header_only_file(tmp_path):
    path = tmp_path / "expenses.csv"

    ensure_csv_with_headers(str(path), "en")

    assert path.exists()
    assert csv_is_header_only(str(path)) is True
    assert read_rows(str(path)) == []


def test_write_and_read_rows_round_trip(tmp_path):
    path = tmp_path / "expenses.csv"

    rows = [
        ["12.34", "food", "groceries", "Milk", "2026-01-15", "Matthew"],
        ["50", "transport", "fuel", "Gas", "2026-01-16", "Matthew"],
    ]

    write_rows(str(path), "en", rows)

    loaded = read_rows(str(path))
    assert loaded == rows


def test_read_rows_skips_english_header(tmp_path):
    path = tmp_path / "expenses.csv"

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(TRANSLATIONS["en"]["csv_headers"])
        w.writerow(["10", "food", "groceries", "Test", "2026-01-01", "Matthew"])

    assert read_rows(str(path)) == [
        ["10", "food", "groceries", "Test", "2026-01-01", "Matthew"]
    ]


def test_read_rows_skips_spanish_header(tmp_path):
    path = tmp_path / "expenses.csv"

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(TRANSLATIONS["es"]["csv_headers"])
        w.writerow(["10", "food", "groceries", "Prueba", "2026-01-01", "Matthew"])

    assert read_rows(str(path)) == [
        ["10", "food", "groceries", "Prueba", "2026-01-01", "Matthew"]
    ]


def test_write_rows_sanitizes_formula_like_text(tmp_path):
    path = tmp_path / "expenses.csv"

    rows = [
        ["10", "food", "groceries", "=BAD()", "2026-01-01", "@name"],
    ]

    write_rows(str(path), "en", rows)
    loaded = read_rows(str(path))

    assert loaded[0][3] == "'=BAD()"
    assert loaded[0][5] == "'@name"

def test_new_csv_action_creates_and_opens_file(qtbot, tmp_path, monkeypatch):
    csv_path = tmp_path / "new_expenses.csv"

    win = MainWindow()
    qtbot.addWidget(win)

    monkeypatch.setattr(
        "expense_tracker_gui.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(csv_path), "CSV (*.csv)"),
    )

    win._on_new()

    assert csv_path.exists()
    assert win.settings.expense_file == str(csv_path)
    assert win.model.rows == []


def test_open_csv_action_loads_existing_file(qtbot, tmp_path, monkeypatch):
    csv_path = tmp_path / "existing_expenses.csv"
    csv_path.write_text(
        "Amount,Category,Subcategory,Description,Date,Name\n"
        "12.34,food,groceries,Milk,2026-01-10,Matthew\n",
        encoding="utf-8",
    )

    win = MainWindow()
    qtbot.addWidget(win)

    monkeypatch.setattr(
        "expense_tracker_gui.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(csv_path), "CSV (*.csv)"),
    )

    win._on_open()

    assert win.settings.expense_file == str(csv_path)
    assert len(win.model.rows) == 1
    assert win.model.rows[0][3] == "Milk"

def test_month_key_from_datetime():
    assert month_key(datetime(2026, 1, 15)) == "2026-01"


def test_month_key_from_valid_strings():
    assert month_key("2026-01") == "2026-01"
    assert month_key("2026-01-15") == "2026-01"


def test_month_to_int_english_and_spanish():
    assert month_to_int("January") == 1
    assert month_to_int("Jan") == 1
    assert month_to_int("enero") == 1
    assert month_to_int("ene") == 1
    assert month_to_int("12") == 12


def test_month_to_int_invalid():
    assert month_to_int("") is None
    assert month_to_int("13") is None
    assert month_to_int("notamonth") is None


def test_normalize_month_input_strict():
    assert _normalize_month_input_to_ym("2026-01") == "2026-01"
    assert _normalize_month_input_to_ym("2026-1") is None
    assert _normalize_month_input_to_ym("Jan") is None
    assert _normalize_month_input_to_ym("2026-01-15") is None


def test_parse_amount_valid_values():
    assert parse_amount("12.34") == 12.34
    assert parse_amount("$12.34") == 12.34
    assert parse_amount("$1,234.56") == 1234.56
    assert parse_amount("(12.34)") == -12.34
    assert parse_amount("-12.34") == -12.34


def test_parse_amount_invalid_values():
    assert parse_amount(None) is None
    assert parse_amount("") is None
    assert parse_amount("abc") is None
    assert parse_amount("$abc") is None