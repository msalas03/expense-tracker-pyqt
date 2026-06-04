from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QMessageBox, QInputDialog

from expense_tracker_gui import MainWindow
from expense_tracker.i18n.translations import TRANSLATIONS
from expense_tracker.services.csv_service import read_rows
from expense_tracker.gui.tabs.browse_tab import refresh_qa_subs, apply_filters
from expense_tracker.gui.tabs.reports_tab import apply_report_filters, compute_reports_data
from expense_tracker.gui.tabs.budget_tab import apply_budget_filters
from expense_tracker.models.settings import (
    AppSettings,
    save_settings,
    load_settings,
)
from expense_tracker.gui.dialogs import ManageTaxonomyDialog


def test_main_window_builds(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    assert win.windowTitle() != ""
    assert win.tabs.count() >= 4



def test_tabs_exist(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    assert win.tabs.count() == 4
    assert win.tab_browse is not None
    assert win.tab_reports is not None
    assert win.tab_budget is not None
    assert win.tab_help is not None


def test_browse_quick_add_controls_exist(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    assert win.qa_amount is not None
    assert win.qa_cat.count() > 0
    assert win.qa_sub is not None
    assert win.qa_date is not None
    assert win.qa_desc is not None
    assert win.qa_name is not None


def test_reports_refresh_with_rows(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.model.rows = [
        ["10", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
        ["20", "food", "restaurants", "Dinner", "2026-01-11", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    y_idx = win.r_year.findText("2026")
    assert y_idx >= 0
    win.r_year.setCurrentIndex(y_idx)

    m_idx = win.r_month.findData(1)
    assert m_idx >= 0
    win.r_month.setCurrentIndex(m_idx)

    apply_report_filters(win)
    qtbot.wait(50)

    assert win.model_by_cat.rowCount() >= 1
    assert win.model_by_sub.rowCount() >= 1


def test_budget_refresh_does_not_crash(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.annual_budgets = {"2026": {"food": 500.0}}
    win.model.rows = [
        ["25", "food", "groceries", "Milk", "2026-01-10", "Matthew"],
    ]
    win.model.layoutChanged.emit()

    y_idx = win.b_year.findText("2026")
    assert y_idx >= 0
    win.b_year.setCurrentIndex(y_idx)

    m_idx = win.b_month.findData(1)
    assert m_idx >= 0
    win.b_month.setCurrentIndex(m_idx)

    apply_budget_filters(win)

    assert win.model_bva.rowCount() >= 1



class DummyCloseEvent:
    def __init__(self):
        self.accepted = False
        self.ignored = False

    def accept(self):
        self.accepted = True

    def ignore(self):
        self.ignored = True


def test_close_event_accepts_when_user_confirms(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    event = DummyCloseEvent()

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    win.closeEvent(event)

    assert event.accepted is True
    assert event.ignored is False


def test_close_event_ignores_when_user_declines(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    event = DummyCloseEvent()

    monkeypatch.setattr(
        "expense_tracker_gui.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    win.closeEvent(event)

    assert event.accepted is False
    assert event.ignored is True



def test_language_switch_to_spanish(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.set_language("es")

    assert win.tabs.tabText(0) == "Explorar"
    assert win.tabs.tabText(1) == "Reportes"
    assert win.tabs.tabText(2) == "Presupuesto"
    assert win.tabs.tabText(3) == "Ayuda"


def test_language_switch_back_to_english(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.set_language("es")
    win.set_language("en")

    assert win.tabs.tabText(0) == "Browse"
    assert win.tabs.tabText(1) == "Reports"
    assert win.tabs.tabText(2) == "Budget"
    assert win.tabs.tabText(3) == "Help"



def test_language_persists_after_reload(qtbot, tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"

    monkeypatch.setattr(
        "expense_tracker.models.settings.SETTINGS_FILE",
        str(settings_path),
    )

    win = MainWindow()
    qtbot.addWidget(win)

    win.set_language("es")

    loaded = load_settings()

    assert loaded.lang == "es"

    # Simulate app restart
    win2 = MainWindow()
    qtbot.addWidget(win2)

    assert win2.lang == "es"
    assert win2.windowTitle() == win2.tr_gui("app_title")



def test_taxonomy_active_category_keys_exist(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    keys = win._active_cat_keys()

    assert keys
    assert "food" in keys
    assert "transport" in keys


def test_quick_add_subcategories_refresh_for_category(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    food_idx = win.qa_cat.findData("food")
    assert food_idx >= 0

    win.qa_cat.setCurrentIndex(food_idx)
    refresh_qa_subs(win)

    sub_keys = [
        win.qa_sub.itemData(i)
        for i in range(win.qa_sub.count())
    ]

    assert "groceries" in sub_keys
    assert "restaurants" in sub_keys



def test_taxonomy_changes_persist(qtbot, tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"

    monkeypatch.setattr(
        "expense_tracker.models.settings.SETTINGS_FILE",
        str(settings_path),
    )

    win = MainWindow()
    qtbot.addWidget(win)

    taxonomy = win.settings.taxonomy

    taxonomy["categories"]["test_cat"] = {
        "en": "Test Category",
        "es": "Categoria Test",
        "active": True,
    }

    taxonomy["subcategories"]["test_sub"] = {
        "en": "Test Sub",
        "es": "Sub Test",
        "active": True,
    }

    taxonomy["category_groups"]["test_cat"] = ["test_sub"]

    win.settings.taxonomy = taxonomy
    save_settings(win.settings)

    loaded = load_settings()

    assert "test_cat" in loaded.taxonomy["categories"]
    assert "test_sub" in loaded.taxonomy["subcategories"]
    assert loaded.taxonomy["category_groups"]["test_cat"] == ["test_sub"]



def patch_settings_file(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(
        "expense_tracker.models.settings.SETTINGS_FILE",
        settings_file,
    )
    return settings_file


def test_username_and_file_persist(tmp_path, monkeypatch):
    patch_settings_file(tmp_path, monkeypatch)

    settings = AppSettings()
    settings.username = "Matthew"
    settings.expense_file = "expenses.csv"

    save_settings(settings)
    loaded = load_settings()

    assert loaded.username == "Matthew"
    assert loaded.expense_file == "expenses.csv"


def test_last_quick_add_values_persist(tmp_path, monkeypatch):
    patch_settings_file(tmp_path, monkeypatch)

    settings = AppSettings()
    settings.last_qa_cat_key = "food"
    settings.last_qa_sub_key = "groceries"

    save_settings(settings)
    loaded = load_settings()

    assert loaded.last_qa_cat_key == "food"
    assert loaded.last_qa_sub_key == "groceries"


def test_budget_templates_persist(tmp_path, monkeypatch):
    patch_settings_file(tmp_path, monkeypatch)

    settings = AppSettings()
    settings.annual_budgets = {
        "2026": {
            "food": 500.0,
        }
    }

    save_settings(settings)
    loaded = load_settings()

    assert loaded.annual_budgets == {
        "2026": {
            "food": 500.0,
        }
    }


def test_income_items_persist(tmp_path, monkeypatch):
    patch_settings_file(tmp_path, monkeypatch)

    settings = AppSettings()
    settings.income_items = [
        {
            "month": "2026-01",
            "employer": "Test Employer",
            "biweekly_amount": 1000,
            "distributions": 2,
            "other_income": 250,
        }
    ]

    save_settings(settings)
    loaded = load_settings()

    assert loaded.income_items == settings.income_items



def test_required_languages_exist():
    assert "en" in TRANSLATIONS
    assert "es" in TRANSLATIONS


def test_csv_headers_have_six_columns():
    for lang in ("en", "es"):
        assert len(TRANSLATIONS[lang]["csv_headers"]) == 6


def test_gui_translation_key_parity():
    en_keys = set(TRANSLATIONS["en"]["gui"].keys())
    es_keys = set(TRANSLATIONS["es"]["gui"].keys())
    assert en_keys == es_keys


def test_category_key_parity():
    assert set(TRANSLATIONS["en"]["categories"]) == set(TRANSLATIONS["es"]["categories"])


def test_subcategory_key_parity():
    assert set(TRANSLATIONS["en"]["subcategories"]) == set(TRANSLATIONS["es"]["subcategories"])


def test_category_group_key_parity():
    assert set(TRANSLATIONS["en"]["category_groups"]) == set(TRANSLATIONS["es"]["category_groups"])


def test_category_groups_reference_existing_subcategories():
    for lang in ("en", "es"):
        sub_keys = set(TRANSLATIONS[lang]["subcategories"])
        for category, group_subs in TRANSLATIONS[lang]["category_groups"].items():
            assert isinstance(group_subs, list)
            missing = set(group_subs) - sub_keys
            assert not missing, f"{lang}:{category} has unknown subcategories: {missing}"



def test_manage_categories_dialog_builds(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    assert dlg.windowTitle()
    assert hasattr(dlg, "tx")
    assert isinstance(dlg.tx, dict)


def test_manage_categories_dialog_has_taxonomy_sections(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    assert "categories" in dlg.tx
    assert "subcategories" in dlg.tx
    assert "category_groups" in dlg.tx

    assert isinstance(dlg.tx["categories"], dict)
    assert isinstance(dlg.tx["subcategories"], dict)
    assert isinstance(dlg.tx["category_groups"], dict)


def test_manage_categories_dialog_loads_existing_categories(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    category_keys = set(dlg.tx["categories"].keys())

    assert "food" in category_keys
    assert "transport" in category_keys


def test_manage_categories_dialog_loads_existing_subcategories(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    subcategory_keys = set(dlg.tx["subcategories"].keys())

    assert "groceries" in subcategory_keys
    assert "fuel" in subcategory_keys


def test_manage_categories_add_category(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    responses = iter([
        ("Test Category", True),
        ("Categoría de Prueba", True),
    ])

    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: next(responses),
    )

    dlg._cat_add()

    added = [
        key for key, node in dlg.tx["categories"].items()
        if node.get("en") == "Test Category"
    ]

    assert len(added) == 1
    assert dlg.tx["categories"][added[0]]["es"] == "Categoría de Prueba"
    assert dlg.tx["categories"][added[0]]["active"] is True
    assert added[0] in dlg.tx["category_groups"]


def test_manage_categories_add_subcategory(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)

    responses = iter([
        ("Test Subcategory", True),
        ("Subcategoría de Prueba", True),
    ])

    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: next(responses),
    )

    dlg._sub_add()

    added = [
        key for key, node in dlg.tx["subcategories"].items()
        if node.get("en") == "Test Subcategory"
    ]

    assert len(added) == 1
    assert dlg.tx["subcategories"][added[0]]["es"] == "Subcategoría de Prueba"
    assert dlg.tx["subcategories"][added[0]]["active"] is True
    assert added[0] in dlg.tx["category_groups"]["food"]


def test_manage_categories_archive_category(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    dlg._cat_archive()

    assert dlg.tx["categories"]["food"]["active"] is False


def test_manage_categories_restore_category(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    dlg.tx["categories"]["food"]["active"] = False
    dlg._refresh_cat_list()

    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    dlg._cat_restore()

    assert dlg.tx["categories"]["food"]["active"] is True


def test_manage_categories_accept_saves_taxonomy(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    dlg.tx["categories"]["food"]["en"] = "Food Updated"

    dlg.accept()

    assert win.settings.taxonomy["categories"]["food"]["en"] == "Food Updated"


def test_main_menus_exist(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    menu_titles = [action.text() for action in win.menuBar().actions()]

    assert win.tr_gui("menu_file") in menu_titles
    assert win.tr_gui("menu_tools") in menu_titles
    assert win.tr_gui("menu_actions") in menu_titles
    assert win.tr_gui("menu_help") in menu_titles


def test_help_menu_action_switches_to_help_tab(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.tabs.setCurrentWidget(win.tab_browse)

    help_menu_action = None
    for action in win.menuBar().actions():
        if action.text() == win.tr_gui("menu_help"):
            help_menu_action = action
            break

    assert help_menu_action is not None

    help_menu = help_menu_action.menu()
    assert help_menu is not None

    help_action = help_menu.actions()[0]
    help_action.trigger()

    assert win.tabs.currentWidget() is win.tab_help


def test_apply_responsive_layout_executes(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win._apply_responsive_layout()

    assert hasattr(win, "_ui_bp_narrow")
    assert hasattr(win, "_ui_bp_very_narrow")


def test_resize_narrow_layout_executes(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.resize(900, 700)
    win._apply_responsive_layout()

    assert win._ui_bp_narrow is True


def test_resize_wide_layout_executes(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    monkeypatch.setattr(
        win.centralWidget(),
        "width",
        lambda: 1200,
    )

    win._apply_responsive_layout()

    assert win._ui_bp_narrow is False
    assert win._ui_bp_very_narrow is False


def test_manage_categories_cannot_archive_last_category(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    # Make food the only active category.
    for key, node in dlg.tx["categories"].items():
        node["active"] = key == "food"

    dlg._refresh_cat_list()

    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)

    called = {"info": False, "confirm": False}

    def fake_info(*args, **kwargs):
        called["info"] = True

    def fake_question(*args, **kwargs):
        called["confirm"] = True
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "information", fake_info)
    monkeypatch.setattr(QMessageBox, "question", fake_question)

    dlg._cat_archive()

    assert called["info"] is True
    assert called["confirm"] is False
    assert dlg.tx["categories"]["food"]["active"] is True


def test_manage_categories_cannot_archive_last_subcategory(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    # Make groceries the only active subcategory.
    for key, node in dlg.tx["subcategories"].items():
        node["active"] = key == "groceries"

    # Select food category.
    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)
    dlg._refresh_sub_list()

    grocery_row = None
    for i in range(dlg.lst_sub.count()):
        item = dlg.lst_sub.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "groceries":
            grocery_row = i
            break

    assert grocery_row is not None
    dlg.lst_sub.setCurrentRow(grocery_row)

    called = {"info": False, "confirm": False}

    def fake_info(*args, **kwargs):
        called["info"] = True

    def fake_question(*args, **kwargs):
        called["confirm"] = True
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "information", fake_info)
    monkeypatch.setattr(QMessageBox, "question", fake_question)

    dlg._sub_archive()

    assert called["info"] is True
    assert called["confirm"] is False
    assert dlg.tx["subcategories"]["groceries"]["active"] is True


def test_manage_categories_edit_category(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)

    monkeypatch.setattr(
        dlg,
        "_input_text",
        lambda *args, **kwargs: "Food Updated",
    )

    dlg._cat_edit()

    assert dlg.tx["categories"]["food"]["en"] == "Food Updated"


def test_manage_categories_edit_subcategory(qtbot, monkeypatch):
    win = MainWindow()
    qtbot.addWidget(win)

    dlg = ManageTaxonomyDialog(win)
    qtbot.addWidget(dlg)

    food_row = None
    for i in range(dlg.lst_cat.count()):
        item = dlg.lst_cat.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "food":
            food_row = i
            break

    assert food_row is not None
    dlg.lst_cat.setCurrentRow(food_row)

    dlg._refresh_sub_list()

    grocery_row = None
    for i in range(dlg.lst_sub.count()):
        item = dlg.lst_sub.item(i)
        if item.data(Qt.ItemDataRole.UserRole) == "groceries":
            grocery_row = i
            break

    assert grocery_row is not None
    dlg.lst_sub.setCurrentRow(grocery_row)

    monkeypatch.setattr(
        dlg,
        "_input_text",
        lambda *args, **kwargs: "Groceries Updated",
    )

    dlg._sub_edit()

    assert dlg.tx["subcategories"]["groceries"]["en"] == "Groceries Updated"


def test_archived_category_removed_from_quick_add(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    assert win.qa_cat.findData("food") >= 0

    win.settings.taxonomy["categories"]["food"]["active"] = False
    win.refresh_taxonomy_ui()

    assert win.qa_cat.findData("food") == -1


def test_corrupt_taxonomy_falls_back_to_seeded_taxonomy(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)

    win.settings.taxonomy = None

    taxonomy = win._taxonomy()

    assert isinstance(taxonomy, dict)
    assert "categories" in taxonomy
    assert "subcategories" in taxonomy
    assert "category_groups" in taxonomy
    assert "food" in taxonomy["categories"]
    assert "groceries" in taxonomy["subcategories"]


def test_full_user_workflow(qtbot, tmp_path, monkeypatch):
    """
    End-to-end smoke test for a normal user flow:
    open/create CSV path, quick add expense, filter Browse,
    refresh Reports, refresh Budget, switch language, and verify persistence.
    """
    win = MainWindow()
    qtbot.addWidget(win)

    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: None,
    )

    csv_path = tmp_path / "expense.csv"
    win.settings.expense_file = str(csv_path)

    # --- Browse / Quick Add ---
    food_idx = win.qa_cat.findData("food")
    assert food_idx >= 0
    win.qa_cat.setCurrentIndex(food_idx)

    groceries_idx = win.qa_sub.findData("groceries")
    assert groceries_idx >= 0
    win.qa_sub.setCurrentIndex(groceries_idx)

    win.qa_amount.setText("42.50")
    win.qa_desc.setText("End to End Groceries")
    win.qa_name.setText("Matthew")
    win.qa_date.setDate(QDate(2026, 1, 10))

    win._quick_add()

    assert len(win.model.rows) == 1
    assert win.model.rows[0][0] == "42.5"
    assert win.model.rows[0][1] == "food"
    assert win.model.rows[0][2] == "groceries"
    assert win.model.rows[0][3] == "End to End Groceries"

    saved_rows = read_rows(str(csv_path))
    assert len(saved_rows) == 1
    assert saved_rows[0][3] == "End to End Groceries"

    # --- Browse filter/status ---
    y_idx = win.f_year.findText("2026")
    assert y_idx >= 0
    win.f_year.setCurrentIndex(y_idx)

    m_idx = win.f_month.findData(1)
    assert m_idx >= 0
    win.f_month.setCurrentIndex(m_idx)

    food_filter_idx = win.f_cat.findData("food")
    assert food_filter_idx >= 0
    win.f_cat.setCurrentIndex(food_filter_idx)

    apply_filters(win)

    assert win.proxy.rowCount() == 1

    # --- Reports ---
    ry_idx = win.r_year.findText("2026")
    assert ry_idx >= 0
    win.r_year.setCurrentIndex(ry_idx)

    rm_idx = win.r_month.findData(1)
    assert rm_idx >= 0
    win.r_month.setCurrentIndex(rm_idx)

    apply_report_filters(win)

    by_cat, by_sub = compute_reports_data(win)

    assert dict(by_cat)[win.cat_label("food")] == 42.5
    assert dict(by_sub)[win.sub_label("groceries")] == 42.5

    # --- Budget ---
    win.settings.annual_budgets = {
        "2026": {
            "food": 100.0,
        }
    }

    win.b_year.setCurrentText("2026")
    b_month_idx = win.b_month.findData(1)
    assert b_month_idx >= 0
    win.b_month.setCurrentIndex(b_month_idx)

    apply_budget_filters(win)

    bva_rows = win.model_bva.rows
    assert bva_rows

    food_bva = next(row for row in bva_rows if row[0] == win.cat_label("food"))
    assert food_bva[1] == 100.0
    assert food_bva[2] == 42.5

    # --- Language switching ---
    win.set_language("es")
    assert win.lang == "es"

    win.set_language("en")
    assert win.lang == "en"

    # --- Settings persistence in current window ---
    assert win.settings.expense_file == str(csv_path)
    assert win.settings.last_qa_cat_key == "food"
    assert win.settings.last_qa_sub_key == "groceries"