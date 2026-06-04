from expense_tracker_gui import MainWindow
from expense_tracker.gui.tabs.reports_tab import apply_report_filters, refresh_reports, compute_reports_data


def test_reports_aggregate_by_category_and_subcategory(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["15", "food", "restaurants", "Lunch", "2026-01-11", "Matthew"],
        ["20", "transport", "fuel", "Gas", "2026-01-12", "Matthew"],
        ["99", "food", "groceries", "Old", "2026-02-01", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    win.r_year.setCurrentText("2026")
    win.r_month.setCurrentIndex(win.r_month.findData(1))

    apply_report_filters(win)
    refresh_reports(win)

    cat_rows = win.model_by_cat.rows
    sub_rows = win.model_by_sub.rows

    assert any(row[0] == win.cat_label("food") and row[1] == 25.0 for row in cat_rows)
    assert any(row[0] == win.cat_label("transport") and row[1] == 20.0 for row in cat_rows)
    assert any(row[0] == win.sub_label("groceries") and row[1] == 10.0 for row in sub_rows)
    assert any(row[0] == win.sub_label("restaurants") and row[1] == 15.0 for row in sub_rows)



def set_reports_filter_month(win, year: str, month: int):
    y_idx = win.r_year.findText(year)
    assert y_idx >= 0
    win.r_year.setCurrentIndex(y_idx)

    m_idx = win.r_month.findData(month)
    assert m_idx >= 0
    win.r_month.setCurrentIndex(m_idx)


def test_reports_filters_limit_report_totals(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["15", "food", "restaurants", "Lunch", "2026-01-11", "Matthew"],
        ["99", "transport", "fuel", "Gas", "2026-02-01", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    set_reports_filter_month(win, "2026", 1)

    food_idx = win.r_cat.findData("food")
    assert food_idx >= 0
    win.r_cat.setCurrentIndex(food_idx)

    apply_report_filters(win)

    by_cat, by_sub = compute_reports_data(win)

    assert by_cat == [(win.cat_label("food"), 25.0)]

    sub_totals = dict(by_sub)
    assert sub_totals[win.sub_label("groceries")] == 10.0
    assert sub_totals[win.sub_label("restaurants")] == 15.0
    assert win.sub_label("fuel") not in sub_totals