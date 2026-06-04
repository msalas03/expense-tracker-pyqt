from PyQt6.QtWidgets import QMessageBox

from expense_tracker_gui import MainWindow
from expense_tracker.i18n.translations import TRANSLATIONS
from expense_tracker.gui.tabs.browse_tab import refresh_qa_subs
from expense_tracker.gui.tabs.reports_tab import apply_report_filters
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