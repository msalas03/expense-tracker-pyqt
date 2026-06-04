from PyQt6.QtWidgets import QMessageBox

from expense_tracker_gui import MainWindow
from expense_tracker.gui.tabs.budget_tab import (
    add_budget_item,
    add_income_item,
    apply_budget_filters,
    compute_actuals_by_category,
    edit_income_selected,
    delete_income_selected,
    ensure_annual_budget_exists_for_year,
)


def test_add_budget_item(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.bt_year.setText("2026")
    win.bt_amount.setText("500")

    if win.bt_cat.count() > 1:
        win.bt_cat.setCurrentIndex(1)

    add_budget_item(win)

    annual = win.settings.annual_budgets
    assert "2026" in annual



def test_add_income_item(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.income_items = []

    win.i_month.setText("2026-01")
    win.i_employer.setText("Test Employer")
    win.i_biweekly.setText("1000")
    win.i_distribs.setCurrentText("2")
    win.i_other.setText("250")

    add_income_item(win)

    assert len(win.settings.income_items) == 1
    item = win.settings.income_items[0]

    assert item["month"] == "2026-01"
    assert item["employer"] == "Test Employer"
    assert item["biweekly_amount"] == 1000
    assert item["distributions"] == 2
    assert item["other_income"] == 250



def set_budget_filter_month(win, year: str, month: int):
    y_idx = win.b_year.findText(year)
    assert y_idx >= 0
    win.b_year.setCurrentIndex(y_idx)

    m_idx = win.b_month.findData(month)
    assert m_idx >= 0
    win.b_month.setCurrentIndex(m_idx)


def test_compute_actuals_by_category_for_selected_month(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["15", "food", "restaurants", "Lunch", "2026-01-11", "Matthew"],
        ["20", "transport", "fuel", "Gas", "2026-01-12", "Matthew"],
        ["99", "food", "groceries", "Old month", "2026-02-01", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    actuals = compute_actuals_by_category(win, 2026, 1)

    assert actuals["food"] == 25.0
    assert actuals["transport"] == 20.0
    assert sum(actuals.values()) == 45.0


def test_budget_vs_actual_rows_include_variance(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {
        "2026": {
            "food": 100.0,
            "transport": 50.0,
        }
    }

    win.model.rows = [
        ["25", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["60", "transport", "fuel", "Gas", "2026-01-11", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    set_budget_filter_month(win, "2026", 1)
    apply_budget_filters(win)

    rows = win.model_bva.rows
    row_map = {category: (budget, actual) for category, budget, actual in rows}

    assert row_map[win.cat_label("food")] == (100.0, 25.0)
    assert row_map[win.cat_label("transport")] == (50.0, 60.0)


def test_budget_year_isolated(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {
        "2025": {"food": 999.0},
        "2026": {"food": 100.0},
    }

    win.model.rows = [
        ["25", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    set_budget_filter_month(win, "2026", 1)
    apply_budget_filters(win)

    rows = win.model_bva.rows
    row_map = {category: (budget, actual) for category, budget, actual in rows}

    assert row_map[win.cat_label("food")] == (100.0, 25.0)
    assert row_map[win.cat_label("food")] != (999.0, 25.0)



def test_budget_vs_actual_calculation(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {"2026": {"food": 500.0}}
    win.model.rows = [
        ["100", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["50", "food", "restaurants", "Lunch", "2026-01-11", "Matthew"],
    ]

    actuals = compute_actuals_by_category(win, 2026, 1)

    assert actuals["food"] == 150.0


def test_budget_variance_calculation(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {"2026": {"food": 500.0}}
    win.model.rows = [
        ["600", "food", "groceries", "Groceries", "2026-01-10", "Matthew"],
    ]

    win.b_year.setCurrentText("2026")
    win.b_month.setCurrentIndex(win.b_month.findData(1))

    apply_budget_filters(win)

    rows = win.model_bva.rows
    assert rows
    category, budget, actual = rows[0]

    assert budget == 500.0
    assert actual == 600.0
    assert actual - budget == 100.0


def test_budget_filter_changes_results(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {"2026": {"food": 500.0}}
    win.model.rows = [
        ["100", "food", "groceries", "Jan Milk", "2026-01-10", "Matthew"],
        ["200", "food", "groceries", "Feb Milk", "2026-02-10", "Matthew"],
    ]

    win.b_year.setCurrentText("2026")
    win.b_month.setCurrentIndex(win.b_month.findData(1))
    apply_budget_filters(win)
    jan_actual = win.model_bva.rows[0][2]

    win.b_month.setCurrentIndex(win.b_month.findData(2))
    apply_budget_filters(win)
    feb_actual = win.model_bva.rows[0][2]

    assert jan_actual == 100.0
    assert feb_actual == 200.0


def test_budget_year_creation(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {}

    monkeypatch.setattr(
        "expense_tracker.gui.tabs.budget_tab.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    result = ensure_annual_budget_exists_for_year(win, 2026)

    assert result is True
    assert "2026" in win.settings.annual_budgets


def test_budget_template_update_confirmation(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {"2026": {"food": 500.0}}

    win.bt_year.setText("2026")
    win.bt_amount.setText("750")

    food_idx = win.bt_cat.findData("food")
    assert food_idx >= 0
    win.bt_cat.setCurrentIndex(food_idx)

    monkeypatch.setattr(
        "expense_tracker.gui.tabs.budget_tab.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        "expense_tracker.gui.tabs.budget_tab.QMessageBox.information",
        lambda *args, **kwargs: None,
    )

    add_budget_item(win)

    assert win.settings.annual_budgets["2026"]["food"] == 750.0


def test_edit_income_selected(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model_income_combined.setRows([
        ("2026-01", "Test Employer", 1000.0, 2, 250.0, 2250.0, 500.0, 1750.0)
    ])

    win.tbl_income_combined.selectRow(0)

    edit_income_selected(win)

    assert win.i_month.text() == "2026-01"
    assert win.i_employer.text() == "Test Employer"
    assert win.i_biweekly.text() == "1000.0"
    assert win.i_distribs.currentText() == "2"
    assert win.i_other.text() == "250.0"


def test_delete_income_selected(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.income_items = [
        {
            "month": "2026-01",
            "employer": "Test Employer",
            "biweekly_amount": 1000,
            "distributions": 2,
            "other_income": 250,
        }
    ]

    win.model_income_combined.setRows([
        ("2026-01", "Test Employer", 1000.0, 2, 250.0, 2250.0, 500.0, 1750.0)
    ])

    win.tbl_income_combined.selectRow(0)

    monkeypatch.setattr(
        "expense_tracker.gui.tabs.budget_tab.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    delete_income_selected(win)

    assert win.settings.income_items == []