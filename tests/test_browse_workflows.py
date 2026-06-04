from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtWidgets import QMessageBox

from expense_tracker_gui import MainWindow

from expense_tracker.gui.tabs.browse_tab import apply_filters, clear_filters, apply_filters
from expense_tracker.gui.tabs.budget_tab import add_income_item
from expense_tracker.gui.dialogs import EditRowDialog
from expense_tracker.services.csv_service import read_rows


def test_browse_filter_by_month_and_category(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["20", "transport", "fuel", "Gas", "2026-01-11", "Matthew"],
        ["30", "food", "restaurants", "Dinner", "2026-02-01", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    y_idx = win.f_year.findText("2026")
    assert y_idx >= 0
    win.f_year.setCurrentIndex(y_idx)

    m_idx = win.f_month.findData(1)
    assert m_idx >= 0
    win.f_month.setCurrentIndex(m_idx)

    food_idx = win.f_cat.findData("food")
    assert food_idx >= 0
    win.f_cat.setCurrentIndex(food_idx)

    apply_filters(win)

    # Force deferred QTimer filtering to process
    qtbot.wait(50)

    assert win.proxy.rowCount() == 1



def test_clear_browse_filters_resets_to_defaults(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.f_name.setText("Matthew")
    win.f_desc.setText("Milk")

    food_idx = win.f_cat.findData("food")
    if food_idx >= 0:
        win.f_cat.setCurrentIndex(food_idx)

    clear_filters(win)

    assert win.f_name.text() == ""
    assert win.f_desc.text() == ""
    assert win.f_cat.currentIndex() == 0
    assert win.f_sub.currentIndex() == 0


def test_quick_add_rejects_invalid_amount(qtbot, monkeypatch, tmp_path):
    win = MainWindow()
    qtbot.addWidget(win)

    csv_path = tmp_path / "expenses.csv"
    win.settings.expense_file = str(csv_path)

    win.qa_amount.setText("abc")
    before = len(win.model.rows)

    win._quick_add()

    assert len(win.model.rows) == before


def test_income_add_upserts_existing_employer_month(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.income_items = []

    win.i_month.setText("2026-01")
    win.i_employer.setText("Test Employer")
    win.i_biweekly.setText("1000")
    win.i_distribs.setCurrentText("2")
    win.i_other.setText("100")
    add_income_item(win)

    win.i_biweekly.setText("1500")
    win.i_other.setText("250")
    add_income_item(win)

    matches = [
        x for x in win.settings.income_items
        if x["month"] == "2026-01" and x["employer"] == "Test Employer"
    ]

    assert len(matches) == 1
    assert matches[0]["biweekly_amount"] == 1500.0
    assert matches[0]["other_income"] == 250.0


def test_apply_filters_updates_status(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    y_idx = win.f_year.findText("2026")
    assert y_idx >= 0
    win.f_year.setCurrentIndex(y_idx)

    m_idx = win.f_month.findData(1)
    assert m_idx >= 0
    win.f_month.setCurrentIndex(m_idx)

    apply_filters(win)

    assert "1" in win.status.currentMessage()



def test_quick_add_requires_csv(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    # Isolate test from persisted user settings
    win.settings.expense_file = ""
    win.model.rows = []

    win.qa_amount.setText("12.34")
    win._quick_add()

    assert len(win.model.rows) == 0



def test_quick_add_rejects_invalid_category_subcategory(qtbot, tmp_path, monkeypatch):
    csv_path = tmp_path / "expenses.csv"

    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.expense_file = str(csv_path)

    captured = {"critical": False}

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.critical",
        lambda *args, **kwargs: captured.update({"critical": True}),
    )

    win.qa_amount.setText("10")
    win.qa_desc.setText("Invalid category/subcategory test")
    win.qa_name.setText("Matthew")

    # Force an invalid pairing: food + fuel
    food_idx = win.qa_cat.findData("food")
    assert food_idx >= 0
    win.qa_cat.setCurrentIndex(food_idx)

    fuel_idx = win.qa_sub.findData("fuel")
    if fuel_idx >= 0:
        win.qa_sub.setCurrentIndex(fuel_idx)
    else:
        win.qa_sub.addItem("Fuel", "fuel")
        win.qa_sub.setCurrentIndex(win.qa_sub.findData("fuel"))

    win._quick_add()

    assert captured["critical"] is True
    assert win.model.rows == []



def set_browse_filter_month(win, year: str, month: int):
    y_idx = win.f_year.findText(year)
    assert y_idx >= 0
    win.f_year.setCurrentIndex(y_idx)

    m_idx = win.f_month.findData(month)
    assert m_idx >= 0
    win.f_month.setCurrentIndex(m_idx)

def test_delete_selected_removes_row(qtbot, tmp_path, monkeypatch):
    csv_path = tmp_path / "expenses.csv"

    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.expense_file = str(csv_path)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["20", "transport", "fuel", "Gas", "2026-01-11", "Matthew"],
    ]

    win._save_model()
    win.model.layoutChanged.emit()

    set_browse_filter_month(win, "2026", 1)

    apply_filters(win)

    # Select first row
    idx = win.proxy.index(0, 0)
    assert idx.isValid()

    win.table.setCurrentIndex(idx)
    win.table.selectionModel().select(
        idx,
        win.table.selectionModel().SelectionFlag.Select
        | win.table.selectionModel().SelectionFlag.Rows,
    )

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    win._delete_selected()

    assert len(win.model.rows) == 1
    remaining_descs = [row[3] for row in win.model.rows]
    assert remaining_descs == ["Milk"]

    rows = read_rows(str(csv_path))
    assert len(rows) == 1


def test_delete_selected_without_selection_does_nothing(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    called = {"info": False}

    def fake_info(*args, **kwargs):
        called["info"] = True

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.information",
        fake_info,
    )

    win._delete_selected()

    assert called["info"] is True


def test_edit_selected_requires_single_row(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    called = {"info": False}

    def fake_info(*args, **kwargs):
        called["info"] = True

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.information",
        fake_info,
    )

    win._edit_selected()

    assert called["info"] is True



def test_edit_selected_updates_selected_row(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    win.table.selectRow(0)

    monkeypatch.setattr(EditRowDialog, "exec", lambda self: self.DialogCode.Accepted)
    monkeypatch.setattr(
        EditRowDialog,
        "values",
        lambda self: ("15.50", "Updated Milk", "2026-01-12", "Matthew"),
    )

    win._edit_selected()

    assert win.model.rows[0] == [
        "15.5",
        "food",
        "groceries",
        "Updated Milk",
        "2026-01-12",
        "Matthew",
    ]



def set_browse_filter_month(win, year: str, month: int):
    y_idx = win.f_year.findText(year)
    assert y_idx >= 0
    win.f_year.setCurrentIndex(y_idx)

    m_idx = win.f_month.findData(month)
    assert m_idx >= 0
    win.f_month.setCurrentIndex(m_idx)

def test_multi_row_delete_removes_selected_visible_rows(qtbot, tmp_path, monkeypatch):
    csv_path = tmp_path / "expenses.csv"

    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.expense_file = str(csv_path)
    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["20", "transport", "fuel", "Gas", "2026-01-11", "Matthew"],
        ["30", "food", "restaurants", "Dinner", "2026-01-12", "Matthew"],
    ]

    win._save_model()
    win.model.layoutChanged.emit()

    set_browse_filter_month(win, "2026", 1)

    apply_filters(win)

    sel = win.table.selectionModel()
    sel.select(
        win.proxy.index(0, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )
    sel.select(
        win.proxy.index(1, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    win._delete_selected()

    remaining_descs = [row[3] for row in win.model.rows]
    assert len(remaining_descs) == 1
    assert remaining_descs[0] in {"Milk", "Gas", "Dinner"}



def test_sorting_changes_visible_row_order(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["30", "transport", "fuel", "Gas", "2026-01-11", "Matthew"],
        ["20", "food", "restaurants", "Dinner", "2026-01-12", "Matthew"],
    ]

    win.model.layoutChanged.emit()

    # Default startup sort = amount descending
    first_idx = win.proxy.index(0, 0)
    src_idx = win.proxy.mapToSource(first_idx)

    assert win.model.rows[src_idx.row()][3] == "Gas"

    # Sort ascending
    win.table.sortByColumn(0, win.table.horizontalHeader().sortIndicatorOrder())

    win.proxy.sort(0)

    first_idx2 = win.proxy.index(0, 0)
    src_idx2 = win.proxy.mapToSource(first_idx2)

    visible_desc = win.model.rows[src_idx2.row()][3]

    assert visible_desc in {"Milk", "Gas", "Dinner"}



def test_totals_popup_shows_filtered_totals(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    captured = {}

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.information",
        lambda parent, title, message: captured.update(
            {"title": title, "message": message}
        ),
    )

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["15", "food", "restaurants", "Lunch", "2026-01-11", "Matthew"],
        ["99", "transport", "fuel", "Gas", "2026-02-01", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    win.f_name.clear()
    win.f_desc.clear()

    food_idx = win.f_cat.findData("food")
    assert food_idx >= 0
    win.f_cat.setCurrentIndex(food_idx)

    y_idx = win.f_year.findText("2026")
    assert y_idx >= 0
    win.f_year.setCurrentIndex(y_idx)

    m_idx = win.f_month.findData(1)
    assert m_idx >= 0
    win.f_month.setCurrentIndex(m_idx)

    win.model.layoutChanged.emit()
    win.proxy.invalidateFilter()

    apply_filters(win)

    assert win.proxy.rowCount() == 2

    win._on_totals()

    msg = captured["message"]

    assert "$25.00" in msg
    assert win.cat_label("food") in msg
    assert win.sub_label("groceries") in msg
    assert win.sub_label("restaurants") in msg
    assert win.sub_label("fuel") not in msg