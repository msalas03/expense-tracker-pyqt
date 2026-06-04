# Imports
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict, List

# Qt imports
from PyQt6.QtCore import (
    Qt, QLocale, QTimer
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QGuiApplication, QCursor
)
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox, QStatusBar,
    QTabWidget, QComboBox, QDialog,
)

# Charts (Matplotlib)
from matplotlib.figure import Figure

# Function imports
from expense_tracker.services.parse_service import (
    parse_amount,
)
from expense_tracker.services.csv_service import (
    ensure_csv_with_headers,
    read_rows,
    csv_is_header_only,
    write_rows,
    _preflight_writable,
)
from expense_tracker.models.settings import (
    load_settings,
    save_settings,
    _log_err,
)
from expense_tracker.gui.dialogs import EditRowDialog, ManageTaxonomyDialog
from expense_tracker.gui.tabs.help_tab import build_help_tab, help_html
from expense_tracker.gui.tabs.reports_tab import (
    build_reports_tab,
    tune_reports_layout,
    apply_report_filters,
    refresh_reports,
    on_report_filter_cat_changed,
)
from expense_tracker.gui.tabs.browse_tab import (
    build_browse_tab,
    tune_browse_layout,
    apply_filters,
    on_filter_cat_changed,
    refresh_qa_subs,
)
from expense_tracker.gui.tabs.budget_tab import (
    build_budget_tab, 
    tune_budget_layout,
    set_budget_filters_to_current,
    apply_budget_filters
)


# ---------------------------
# Load TRANSLATIONS (GUI-only)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure local module imports work when launched from a different CWD
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from expense_tracker.i18n.translations import TRANSLATIONS


# ---------------------------
# Settings & helpers
# ---------------------------
def _seed_taxonomy_from_translations(lang: str) -> dict:
    """
    Build a taxonomy dict from TRANSLATIONS for first-run initialization.
    Keys remain stable; labels are stored in both EN/ES when possible.
    """
    # default to English block for missing pieces
    t_en = TRANSLATIONS.get("en", {})
    t_es = TRANSLATIONS.get("es", {})
    t_lang = TRANSLATIONS.get(lang, t_en)

    cats_en = (t_en.get("categories") or {})
    cats_es = (t_es.get("categories") or {})
    subs_en = (t_en.get("subcategories") or {})
    subs_es = (t_es.get("subcategories") or {})
    groups  = (t_lang.get("category_groups") or {})  # keys are structural, not language-specific

    taxonomy = {
        "categories": {},
        "subcategories": {},
        "category_groups": {},
    }

    # categories
    for k, label_en in cats_en.items():
        taxonomy["categories"][k] = {
            "en": label_en,
            "es": cats_es.get(k, label_en),
            "active": True,
        }

    # subcategories
    for k, label_en in subs_en.items():
        taxonomy["subcategories"][k] = {
            "en": label_en,
            "es": subs_es.get(k, label_en),
            "active": True,
        }

    # groups: category -> list[sub_key]
    for ck, sub_keys in groups.items():
        if isinstance(sub_keys, list):
            taxonomy["category_groups"][ck] = list(sub_keys)
        else:
            taxonomy["category_groups"][ck] = []

    return taxonomy

def _set_high_dpi_policy_qt6() -> None:
    """Set a helpful high-DPI policy when running under PyQt6.

    Safe to call in mixed Qt environments; it will silently no-op if the
    required classes/attributes are not present.
    """
    try:
        # Local imports to avoid import-time dependency
        from PyQt6.QtGui import QGuiApplication
        from PyQt6.QtCore import Qt
    except ImportError:
        # PyQt6 not available — nothing to do
        return

    # Use attribute checks rather than broad try/except to avoid hiding bugs
    try:
        # QGuiApplication.setHighDpiScaleFactorRoundingPolicy exists in Qt 6.4+
        if hasattr(QGuiApplication, "setHighDpiScaleFactorRoundingPolicy") and hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
            QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
    except (AttributeError, TypeError) as e:
        # If API differs on this platform/version, log and continue
        _log_err("Failed to set high-DPI rounding policy", e)

# ---------------------------
# Main Window
# ---------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # One-time warning mechanism
        self._load_warnings_shown = set()
         # Load settings & language first
        self.settings = load_settings()
        save_settings(self.settings)
        self.lang = self.settings.lang if self.settings.lang in TRANSLATIONS else "en"
        self._i18n = []  # list of tuples: (widget, setter_name, translation_key)

        # --- Taxonomy: seed from TRANSLATIONS on first run ---
        if not isinstance(self.settings.taxonomy, dict) or not self.settings.taxonomy:
            self.settings.taxonomy = _seed_taxonomy_from_translations(self.lang)
            save_settings(self.settings)

        # Now it's safe to translate
        self.setWindowTitle(self.tr_gui("app_title"))
        scr = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        screen = scr.availableGeometry() if scr else None
        if screen:
            self.resize(min(1100, screen.width()), min(800, screen.height()))

        # --- SIZE GUARDRAILS ---
        self.setMinimumSize(900, 600)     # prevents layout collapse
        self.setMaximumWidth(1400)        # prevents runaway width on large monitors

        # Qt6 removed AA_UseHighDpiPixmaps; keep it for Qt5 compatibility only.
        attr = getattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps", None)
        if attr is not None:
            QApplication.setAttribute(attr, True)

        headers = TRANSLATIONS[self.lang]["csv_headers"][:6]

        # Central widget: tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Build tabs
        build_browse_tab(self, headers)
        build_reports_tab(self)
        build_budget_tab(self)
        build_help_tab(self)
        # Refresh Budget tab only when user navigates to it (prevents startup prompts)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Menus + actions
        self._build_menus()

        # Repsonsive App Layout
        self._apply_responsive_layout()
        self._center_on_screen()

        # Apply Fusion style for consistent macOS look
        import platform
        if platform.system() != "Darwin":
            QApplication.setStyle("Fusion")

        # Seed
        self._update_status()

    # ---- GUI Translations ---- 
    def tr_gui(self, key: str) -> str:
        """Translate a GUI string; fall back to English or the key itself."""
        lang = getattr(self, "lang", "en")
        lang_block = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"])
        gui = lang_block.get("gui", {})
        return gui.get(key, TRANSLATIONS["en"].get("gui", {}).get(key, key))

    # ---- Taxonomy helpers ----
    def _taxonomy(self) -> dict:
        tx = getattr(self.settings, "taxonomy", None)
        if isinstance(tx, dict) and tx:
            return tx
        # fallback if settings got corrupted
        return _seed_taxonomy_from_translations(self.lang)

    def cat_label(self, cat_key: str) -> str:
        t = self._taxonomy()
        node = (t.get("categories") or {}).get(cat_key) or {}
        if isinstance(node, dict):
            return node.get(self.lang) or node.get("en") or cat_key
        return cat_key

    def sub_label(self, sub_key: str) -> str:
        t = self._taxonomy()
        node = (t.get("subcategories") or {}).get(sub_key) or {}
        if isinstance(node, dict):
            return node.get(self.lang) or node.get("en") or sub_key
        return sub_key

    def _active_cat_keys(self) -> list[str]:
        t = self._taxonomy()
        cats = t.get("categories") or {}
        keys = []
        for k, node in cats.items():
            if isinstance(node, dict) and node.get("active", True):
                keys.append(k)
        return keys

    def _active_sub_keys(self) -> list[str]:
        t = self._taxonomy()
        subs = t.get("subcategories") or {}
        keys = []
        for k, node in subs.items():
            if isinstance(node, dict) and node.get("active", True):
                keys.append(k)
        return keys

    def _subs_for_cat(self, cat_key: str) -> list[str]:
        t = self._taxonomy()
        groups = t.get("category_groups") or {}
        raw = groups.get(cat_key, []) or []
        if not isinstance(raw, list):
            raw = []
        active_subs = set(self._active_sub_keys())
        return [sk for sk in raw if sk in active_subs]

    def resolve_cat_key(self, text_or_key: str) -> str:
        """Accepts either a key or a visible label; returns a stable key or '' if unknown."""
        s = (text_or_key or "").strip()
        if not s:
            return ""
        t = self._taxonomy()
        cats = t.get("categories") or {}
        if s in cats:
            node = cats.get(s) or {}
            if not isinstance(node, dict) or node.get("active", True):
                return s
            return ""
        # match label in current lang (fallback en)
        needle = s.casefold()
        for k, node in cats.items():
            if not isinstance(node, dict) or not node.get("active", True):
                continue
            lab = (node.get(self.lang) or node.get("en") or k)
            if (lab or "").casefold() == needle:
                return k
        return ""

    def resolve_sub_key(self, text_or_key: str) -> str:
        """Accepts either a key or a visible label; returns a stable key or '' if unknown."""
        s = (text_or_key or "").strip()
        if not s:
            return ""
        t = self._taxonomy()
        subs = t.get("subcategories") or {}
        if s in subs:
            node = subs.get(s) or {}
            if not isinstance(node, dict) or node.get("active", True):
                return s
            return ""
        needle = s.casefold()
        for k, node in subs.items():
            if not isinstance(node, dict) or not node.get("active", True):
                continue
            lab = (node.get(self.lang) or node.get("en") or k)
            if (lab or "").casefold() == needle:
                return k
        return ""

    def _combo_key(self, cb: QComboBox, kind: str) -> str:
        """
        Returns selected key from combobox userData; if user typed text, resolves via taxonomy.
        kind: 'cat' or 'sub'
        """
        data = cb.currentData()
        if isinstance(data, str) and data:
            return data
        txt = (cb.currentText() or "").strip()
        if kind == "cat":
            return self.resolve_cat_key(txt)
        return self.resolve_sub_key(txt)

    # --- Screen Center ---
    def _center_on_screen(self) -> None:
        # Prefer the screen under the cursor (best UX on multi-monitor)
        scr = QGuiApplication.screenAt(QCursor.pos())

        # Fallback to the screen Qt assigned to this window
        if scr is None:
            try:
                scr = self.screen()
            except Exception:
                scr = None

        # Final fallback
        if scr is None:
            scr = QGuiApplication.primaryScreen()

        if scr is None:
            return

        ag = scr.availableGeometry()
        fg = self.frameGeometry()
        fg.moveCenter(ag.center())
        self.move(fg.topLeft())

    # --- Pie Sizing ---
    def _layout_pie_with_legend(self, fig: Figure, ax, wedges, legend_labels: list[str]) -> None:
        """
        Reserve figure space for an external legend so the pie does not shrink unpredictably.
        Uses manual axes positioning (do not combine with tight_layout / constrained_layout).
        """
        n = len(legend_labels)

        # How much width to reserve for legend (tune as desired)
        # More items => slightly more reserved space (cap it)
        legend_frac = min(0.45, 0.28 + 0.012 * min(n, 10))  # 0.28..0.40-ish typical

        left = 0.06
        bottom = 0.08
        top = 0.92
        pie_width = 1.0 - left - legend_frac - 0.04  # keep a small right gutter

        if pie_width < 0.40:  # safety
            pie_width = 0.40

        ax.set_position([left, bottom, pie_width, top - bottom])
        ax.set_aspect("equal", adjustable="box")

        # Remove any old legend and recreate (prevents stacking)
        old_leg = ax.get_legend()
        if old_leg:
            old_leg.remove()

        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),   # sit in reserved legend column
            borderaxespad=0.0,
            frameon=False,
            fontsize="small",
            handlelength=1.2,
            labelspacing=0.6,
        )

    # ---- Tabs ----
    def _apply_responsive_layout(self) -> None:
        """Single source of truth for layout sizing across tabs."""
        # Central width is best approximation of usable space
        w = self.centralWidget().width() if self.centralWidget() else self.width()

        # Breakpoints (tune once for the whole app)
        self._ui_bp_very_narrow = (w < 920)
        self._ui_bp_narrow = (w < 1050)

        # Apply per-tab tuning if those tabs are built
        tune_browse_layout(self)
        tune_reports_layout(self)
        tune_budget_layout(self)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_responsive_layout()

        # Only redraw. Do NOT call tight_layout here; it breaks pie+legend sizing.
        for name in ("canvas_bar", "canvas_pie", "canvas_bbar", "canvas_bpie"):
            c = getattr(self, name, None)
            if c is not None:
                c.draw_idle()

    def _on_tab_changed(self, idx: int) -> None:
        try:
            if self.tabs.widget(idx) is self.tab_budget:
                set_budget_filters_to_current(self)
                apply_budget_filters(self)
        except Exception as e:
            _log_err("Budget tab refresh failed", e)

    # ---- Menus ----
    def _build_menus(self):
        menubar = self.menuBar()
        menubar.clear()
        file_menu = menubar.addMenu(self.tr_gui("menu_file"))
        menu_tools = menubar.addMenu(self.tr_gui("menu_tools"))

        # --- Language submenu ---
        menu_lang = menu_tools.addMenu(self.tr_gui("menu_language"))

        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)

        act_lang_en = QAction(self.tr_gui("menu_language_english"), self)
        act_lang_en.setCheckable(True)
        act_lang_en.setChecked(self.lang == "en")
        act_lang_en.triggered.connect(lambda: self.set_language("en"))

        act_lang_es = QAction(self.tr_gui("menu_language_spanish"), self)
        act_lang_es.setCheckable(True)
        act_lang_es.setChecked(self.lang == "es")
        act_lang_es.triggered.connect(lambda: self.set_language("es"))

        lang_group.addAction(act_lang_en)
        lang_group.addAction(act_lang_es)
        menu_lang.addAction(act_lang_en)
        menu_lang.addAction(act_lang_es)

        act_manage = QAction(self.tr_gui("menu_manage_categories"), self)
        act_manage.triggered.connect(self.open_manage_categories)
        # Add to an existing menu (Settings or Tools); if none, add to Help or File:
        menu_tools.addAction(act_manage)

        act_new = QAction(self.tr_gui("menu_file_new_csv"), self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self._on_new)
        file_menu.addAction(act_new)

        act_open = QAction(self.tr_gui("menu_file_open_csv"), self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self._on_open)
        file_menu.addAction(act_open)

        file_menu.addSeparator()
        act_exit = QAction(self.tr_gui("menu_file_exit"), self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Actions (browse)
        actions = menubar.addMenu(self.tr_gui("menu_actions"))
        act_totals = QAction(self.tr_gui("menu_actions_totals"), self)
        act_totals.setShortcut("Ctrl+T")
        act_totals.triggered.connect(self._on_totals)
        actions.addAction(act_totals)

        # Help menu
        help_menu = menubar.addMenu(self.tr_gui("menu_help"))
        act_help = QAction(self.tr_gui("menu_help_item"), self)
        act_help.setShortcut("F1")
        def _go_help():
           self.tabs.setCurrentWidget(self.tab_help)
        help_menu.addAction(act_help)
        act_help.triggered.connect(_go_help)

    # ---- File ops ----
    def _on_new(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr_gui("dlg_new_csv_title"),
            "",
            "CSV (*.csv)"
        )
        if not path:
            return
        if not _preflight_writable(path):
            QMessageBox.critical(
                self,
                self.tr_gui("dlg_error_title"),
                self.tr_gui("msg_location_not_writable"),
            )
            return
        ensure_csv_with_headers(path, self.lang)
        self._open_path(path)

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr_gui("dlg_open_csv_title"),
            "",
            "CSV (*.csv)"
        )
        if not path:
            return
        self._open_path(path)

    def _open_path(self, path: str):
        self.settings.expense_file = path
        save_settings(self.settings)
        self._reload()

    def _reload(self):
        path = self.settings.expense_file
        self.model.rows = read_rows(path)
        self.model.layoutChanged.emit()
        if hasattr(self, "proxy"):
            apply_filters(self)

        self._update_status()

        # Warn if file exists and has content but parsed to zero rows
        try:
            if (
                path
                and os.path.exists(path)
                and os.path.getsize(path) > 0
                and len(self.model.rows) == 0
                and not csv_is_header_only(path)
            ):
                self._warn_once(
                    "csv_parse_empty",
                    self.tr_gui("dlg_info_title"),
                    self.tr_gui("msg_csv_loaded_empty") if "msg_csv_loaded_empty" in TRANSLATIONS[self.lang].get("gui", {}) 
                    else "The CSV file was opened, but no rows could be parsed. The file may be malformed or use unexpected headers.",
                )
        except Exception as e:
            _log_err("Post-reload CSV size check failed", e)

        if hasattr(self, "model_by_cat"):
            refresh_reports(self)

    def _quick_add(self):
        if not self.settings.expense_file:
            QMessageBox.information(
                self,
                self.tr_gui("dlg_info_title"),
                self.tr_gui("msg_no_csv_open"),
            )
            return

        amt = parse_amount(self.qa_amount.text())
        if amt is None:
            QMessageBox.critical(
                self,
                self.tr_gui("dlg_error_title"),
                self.tr_gui("msg_invalid_amount"),
            )
            return

        # Read date from QDateEdit
        date_str = self.qa_date.date().toString("yyyy-MM-dd")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            QMessageBox.critical(
                self,
                self.tr_gui("dlg_error_title"),
                self.tr_gui("msg_invalid_date"),
            )
            return

        cat_key = self._combo_key(self.qa_cat, "cat")
        sub_key = self._combo_key(self.qa_sub, "sub")

        if not cat_key or not sub_key or (sub_key not in self._subs_for_cat(cat_key)):
            QMessageBox.critical(
                self,
                self.tr_gui("dlg_error_title"),
                self.tr_gui("msg_invalid_cat_sub"),
            )
            return

        # Get name (fallback to username)
        entered_name = (self.qa_name.text() or "").strip()
        name_value = entered_name if entered_name else (self.settings.username or "User")

        if not _preflight_writable(self.settings.expense_file):
            QMessageBox.critical(
                self,
                self.tr_gui("dlg_error_title"),
                self.tr_gui("msg_csv_not_writable"), 
            )
            return

        row = [f"{amt}", cat_key, sub_key, (self.qa_desc.text() or "").strip(), date_str, name_value]
        self.model.rows.append(row)

        try:
            write_rows(self.settings.expense_file, self.lang, self.model.rows)
            QMessageBox.information(
                self,
                self.tr_gui("dlg_info_title"),
                self.tr_gui("msg_expense_saved"),
            )
        except Exception as e:
            # Roll back the append on failure
            self.model.rows.pop()
            QMessageBox.critical(
                self,
                self.tr_gui("dlg_error_title"),
                self.tr_gui("msg_save_failed").format(error=e),
            )
            return

        # Clear only amount/desc; keep name as last used (handy for next add)
        self.qa_amount.clear()
        self.qa_desc.clear()

        # Refresh views without re-reading from disk
        self.model.layoutChanged.emit()
        self._update_status()

        # Refresh heavier tabs only when visible to avoid surprise modal prompts
        # and UI stalls during Quick Add.
        current = self.tabs.currentWidget()
        if current is getattr(self, "tab_reports", None) and hasattr(self, "model_by_cat"):
            refresh_reports(self)
        elif current is getattr(self, "tab_budget", None):
            apply_budget_filters(self)

        self.settings.last_qa_cat_key = cat_key
        self.settings.last_qa_sub_key = sub_key
        save_settings(self.settings)

    def refresh_taxonomy_ui(self):
        """
        Repopulate all category/subcategory combo boxes from current settings.taxonomy.
        Keep current selections where possible.
        """
        # --- Browse filters
        if hasattr(self, "f_cat") and hasattr(self, "f_sub"):
            prev_cat = self._combo_key(self.f_cat, "cat")
            prev_sub = self._combo_key(self.f_sub, "sub")

            self.f_cat.blockSignals(True)
            self.f_cat.clear()
            self.f_cat.addItem("", "")
            cat_keys = sorted(self._active_cat_keys(), key=lambda k: (self.cat_label(k) or k).casefold())
            for ck in cat_keys:
                self.f_cat.addItem(self.cat_label(ck), ck)
            self.f_cat.blockSignals(False)

            if prev_cat:
                idx = self.f_cat.findData(prev_cat)
                if idx >= 0:
                    self.f_cat.setCurrentIndex(idx)

            # refresh sub list based on selected cat
            on_filter_cat_changed(self, self.f_cat.currentText())
            if prev_sub:
                idx = self.f_sub.findData(prev_sub)
                if idx >= 0:
                    self.f_sub.setCurrentIndex(idx)

        # --- Reports filters
        if hasattr(self, "r_cat") and hasattr(self, "r_sub"):
            prev_cat = self._combo_key(self.r_cat, "cat")
            prev_sub = self._combo_key(self.r_sub, "sub")

            self.r_cat.blockSignals(True)
            self.r_cat.clear()
            self.r_cat.addItem("", "")
            cat_keys = sorted(self._active_cat_keys(), key=lambda k: (self.cat_label(k) or k).casefold())
            for ck in cat_keys:
                self.r_cat.addItem(self.cat_label(ck), ck)
            self.r_cat.blockSignals(False)

            if prev_cat:
                idx = self.r_cat.findData(prev_cat)
                if idx >= 0:
                    self.r_cat.setCurrentIndex(idx)

            on_report_filter_cat_changed(self, self.r_cat.currentText())
            if prev_sub:
                idx = self.r_sub.findData(prev_sub)
                if idx >= 0:
                    self.r_sub.setCurrentIndex(idx)

        # --- Quick Add
        if hasattr(self, "qa_cat") and hasattr(self, "qa_sub"):
            prev_cat = self._combo_key(self.qa_cat, "cat")
            prev_sub = self._combo_key(self.qa_sub, "sub")

            self.qa_cat.blockSignals(True)
            self.qa_cat.clear()
            cat_keys = sorted(self._active_cat_keys(), key=lambda k: (self.cat_label(k) or k).casefold())
            for ck in cat_keys:
                self.qa_cat.addItem(self.cat_label(ck), ck)
            self.qa_cat.blockSignals(False)

            if prev_cat:
                idx = self.qa_cat.findData(prev_cat)
                if idx >= 0:
                    self.qa_cat.setCurrentIndex(idx)

            refresh_qa_subs(self)
            if prev_sub:
                idx = self.qa_sub.findData(prev_sub)
                if idx >= 0:
                    self.qa_sub.setCurrentIndex(idx)

        # --- Budget add item
        if hasattr(self, "bt_cat"):
            prev_cat = self._combo_key(self.bt_cat, "cat")
            self.bt_cat.blockSignals(True)
            self.bt_cat.clear()
            self.bt_cat.addItem("", "")
            cat_keys = sorted(self._active_cat_keys(), key=lambda k: (self.cat_label(k) or k).casefold())
            for ck in cat_keys:
                self.bt_cat.addItem(self.cat_label(ck), ck)
            self.bt_cat.blockSignals(False)

            if prev_cat:
                idx = self.bt_cat.findData(prev_cat)
                if idx >= 0:
                    self.bt_cat.setCurrentIndex(idx)

    def set_language(self, lang: str) -> None:
        lang = (lang or "").strip().lower()
        if lang not in TRANSLATIONS or lang == self.lang:
            return

        self.lang = lang
        self.settings.lang = lang
        save_settings(self.settings)

        # keep proxies consistent
        if hasattr(self, "proxy"):
            self.proxy.setLanguage(lang)
        if hasattr(self, "report_proxy"):
            self.report_proxy.setLanguage(lang)

        self._retranslate_ui()

    # ---- Totals popup (Browse) ----
    def _on_totals(self):
        # Gather filtered rows by iterating visible proxy rows
        filtered: List[List[str]] = []
        for pr in range(self.proxy.rowCount()):
            src_index = self.proxy.mapToSource(self.proxy.index(pr, 0))
            if src_index.isValid():
                filtered.append(self.model.rows[src_index.row()])
        if not filtered:
            QMessageBox.information(
                self,
                self.tr_gui("dlg_totals_title"),
                self.tr_gui("msg_totals_none"),
            )
            return

        lang = self.lang
        cat_labels = TRANSLATIONS[lang]["categories"]
        sub_labels = TRANSLATIONS[lang]["subcategories"]
        mdata = self.f_month.currentData()
        month_num = int(mdata) if mdata is not None else None
        month_names = {
            "en": [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            "es": [
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre",
            ],
        }
        month_label = month_names.get(lang, month_names["en"])[month_num - 1] if month_num else None

        overall = 0.0
        by_cat: Dict[str, float] = {}
        by_cat_sub: Dict[str, Dict[str, float]] = {}
        for row in filtered:
            try:
                amt = parse_amount(row[0])
                if amt is None: continue
            except Exception:
                continue
            ckey, skey = row[1], row[2]
            overall += amt
            by_cat[ckey] = by_cat.get(ckey, 0.0) + amt
            by_cat_sub.setdefault(ckey, {})
            by_cat_sub[ckey][skey] = by_cat_sub[ckey].get(skey, 0.0) + amt

        header = (f"Overall Total: ${overall:.2f}" if lang == "en" else f"Total general: ${overall:.2f}")
        if month_label:
            header += (f"  (Month: {month_label})" if lang == "en" else f"  (Mes: {month_label})")

        lines: List[str] = [header, ""]
        # Use taxonomy labels for display and sorting
        for ckey in sorted(by_cat.keys(), key=lambda k: (self.cat_label(k) or k).lower()):
            c_label = self.cat_label(ckey)
            c_total = by_cat[ckey]
            lines.append(f"{c_label}: ${c_total:.2f}")
            for skey in sorted(by_cat_sub.get(ckey, {}).keys(), key=lambda k: (self.sub_label(k) or k).lower()):
                s_label = self.sub_label(skey)
                s_total = by_cat_sub[ckey][skey]
                lines.append(f"  • {s_label}: ${s_total:.2f}")

            lines.append("")
        QMessageBox.information(self, self.tr_gui("dlg_totals_title"), "\n".join(lines).rstrip())

    def _save_model(self):
        """Persist current model rows to CSV and refresh status."""
        if not self.settings.expense_file:
            return
        try:
            write_rows(self.settings.expense_file, self.lang, self.model.rows)
            self._update_status()
            if hasattr(self, "model_by_cat"):
                refresh_reports(self)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")

    def _selected_source_rows(self) -> List[int]:
        """Return selected row indexes in the *source* model order (unique, sorted desc)."""
        sel = self.table.selectionModel().selectedRows()  # proxy indexes
        src_rows = []
        for proxy_index in sel:
            src_index = self.proxy.mapToSource(proxy_index)
            if src_index.isValid():
                src_rows.append(src_index.row())
        return sorted(set(src_rows), reverse=True)  # delete bottom-up

    def _edit_selected(self):
        rows = self._selected_source_rows()
        if len(rows) != 1:
            QMessageBox.information(
                self,
                self.tr_gui("dlg_info_title"),
                self.tr_gui("msg_edit_select_one"),
            )
            return
        r = rows[0]
        row_data = self.model.rows[r]

        dlg = EditRowDialog(self, row_data, self.tr_gui)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            amt, desc, date_str, name = dlg.values()
            # Extra guard (setData also validates)
            try:
                float(str(amt).replace("$", "").replace(",", ""))
                datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                QMessageBox.critical(
                    self,
                    self.tr_gui("dlg_error_title"),
                    self.tr_gui("msg_invalid_amount"),  
                )
                return

            # Apply via model APIs (triggers dataChanged)
            self.model.setData(self.model.index(r, 0), amt)
            self.model.setData(self.model.index(r, 3), desc)
            self.model.setData(self.model.index(r, 4), date_str)
            self.model.setData(self.model.index(r, 5), name)

            self._save_model()

    def _delete_selected(self):
        rows = self._selected_source_rows()
        if not rows:
            QMessageBox.information(
                self,
                self.tr_gui("dlg_info_title"),
                self.tr_gui("msg_delete_select"),
            )
            return
        if QMessageBox.question(
                self,
                self.tr_gui("dlg_confirm_delete_title"),
                self.tr_gui("msg_confirm_delete_body").format(count=len(rows))
            ) != QMessageBox.StandardButton.Yes:
                return

        self.model.layoutAboutToBeChanged.emit()
        for r in rows:
            if 0 <= r < len(self.model.rows):
                del self.model.rows[r]
        self.model.layoutChanged.emit()

        self._save_model()

    def _table_context_menu(self, pos):
        menu = QMenu(self)
        act_edit = QAction(self.tr_gui("browse_edit_selected"), self)
        act_delete = QAction(self.tr_gui("browse_delete_selected"), self)
        act_edit.triggered.connect(self._edit_selected)
        act_delete.triggered.connect(self._delete_selected)
        menu.addAction(act_edit); menu.addAction(act_delete)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    # ---- Close confirmation ----
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            self.tr_gui("dlg_confirm_exit_title"),
            self.tr_gui("msg_close_confirm_body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    # ---- Status ----
    def _update_status(self):
        total = 0.0
        visible = self.proxy.rowCount()

        # Sum visible rows via proxy enumeration
        for pr in range(self.proxy.rowCount()):
            src_index = self.proxy.mapToSource(self.proxy.index(pr, 0))
            if not src_index.isValid():
                continue
            try:
                total += parse_amount(self.model.rows[src_index.row()][0])
            except Exception:
                pass

        template = self.tr_gui("status_rows_total")
        self.status.showMessage(template.format(rows=visible, total=total))

    # ---- Warning ----
    def _warn_once(self, key: str, title: str, msg: str) -> None:
        if key in self._load_warnings_shown:
            return
        self._load_warnings_shown.add(key)
        QMessageBox.warning(self, title, msg)
        
    # ---- Categories opening dialog ----
    def open_manage_categories(self):
        dlg = ManageTaxonomyDialog(self)
        if dlg.exec():
            # taxonomy saved in dlg.accept()
            self.refresh_taxonomy_ui()
            # reapply filters so views remain consistent
            if hasattr(self, "proxy"):
                apply_filters(self)
            if hasattr(self, "report_proxy"):
                apply_report_filters(self)

    # ---- Live language switching helpers ----
    def _bind_text(self, widget, setter: str, key: str):
        """
        Register widget text binding for live language switching.
        setter: "setText" or "setTitle"
        """
        if not hasattr(self, "_i18n"):
            self._i18n = []
        self._i18n.append((widget, setter, key))
        getattr(widget, setter)(self.tr_gui(key))

    def _retranslate_ui(self):
        # Window title + tabs
        self.setWindowTitle(self.tr_gui("app_title"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_browse), self.tr_gui("tab_browse"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_reports), self.tr_gui("tab_reports"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_budget), self.tr_gui("tab_budget"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_help), self.tr_gui("tab_help"))

        # Bound widget texts
        for w, setter, key in getattr(self, "_i18n", []):
            try:
                getattr(w, setter)(self.tr_gui(key))
            except Exception:
                pass

        # Menus must be rebuilt (their titles are not simple widgets)
        self._build_menus()

        # Taxonomy-driven combo labels
        self.refresh_taxonomy_ui()

        # Reports table headers
        if hasattr(self, "model_by_cat"):
            self.model_by_cat.setHeaders([self.tr_gui("reports_header_category"), self.tr_gui("reports_header_total")])
        if hasattr(self, "model_by_sub"):
            self.model_by_sub.setHeaders([self.tr_gui("reports_header_subcategory"), self.tr_gui("reports_header_total")])

        # Budget headers
        if hasattr(self, "model_bva"):
            self.model_bva.setHeaders([
                self.tr_gui("budget_bva_header_category"),
                self.tr_gui("budget_bva_header_budget"),
                self.tr_gui("budget_bva_header_actual"),
                self.tr_gui("budget_bva_header_variance"),
            ])
        if hasattr(self, "model_income_combined"):
            self.model_income_combined.setHeaders([
                self.tr_gui("budget_income_month"),
                self.tr_gui("budget_income_header_employer"),
                self.tr_gui("budget_income_header_biweekly"),
                self.tr_gui("budget_income_header_dists"),
                self.tr_gui("budget_income_header_other"),
                self.tr_gui("budget_income_header_month_total"),
                self.tr_gui("budget_income_header_expense_total"),
                self.tr_gui("budget_income_header_variance"),
            ])
        # Budget Breakdown table headers
        if hasattr(self, "model_bud"):
            self.model_bud.setHeaders([
                self.tr_gui("reports_header_category"),
                self.tr_gui("budget_bva_header_budget"),
            ])

        # Browse table headers (CSV headers)
        if hasattr(self, "model"):
            csv_hdrs = TRANSLATIONS[self.lang]["csv_headers"][:6]
            # Some environments prefer explicit strings rather than raw TRANSLATIONS entries;
            # use them directly so CSV header labels match file format.
            self.model.setHeaders(csv_hdrs)
            # Also update table view header resize if needed
            if hasattr(self, "table"):
                try:
                    self.table.horizontalHeader().reset()  # attempt to refresh header visuals
                except Exception:
                    pass

        # Help
        if hasattr(self, "help_view"):
            self.help_view.setHtml(help_html(self))

        # Redraw dependent outputs
        self._update_status()
        if hasattr(self, "model_by_cat"):
            refresh_reports(self)
        if hasattr(self, "model_bva"):
            apply_budget_filters(self)


# ---------------------------
# Entry point
# ---------------------------
def main():
    # macOS niceties: unify decimals, enable native menu bar integration
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
    _set_high_dpi_policy_qt6()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    QTimer.singleShot(0, win._center_on_screen)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()