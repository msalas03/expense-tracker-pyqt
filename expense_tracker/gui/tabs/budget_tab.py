from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QLabel, QGridLayout, QGroupBox, QWidget, QLineEdit, QComboBox, QPushButton, QSizePolicy, 
    QHeaderView, QTableView, QHBoxLayout, QMessageBox
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from expense_tracker.models.table_models import (
    ExpenseTableModel,
    SimpleTableModel,
    BudgetVsActualModel,
    IncomeCombinedModel,
)
from expense_tracker.models.settings import save_settings
from expense_tracker.services.parse_service import (
    parse_amount,
    _normalize_month_input_to_ym,
)



@dataclass
class IncomeItem:
    month: str         # 'YYYY-MM'
    employer: str      # employer name
    biweekly_amount: float
    distributions: int # 2 or 3
    other_income: float

def build_budget_tab(win) -> None:
        win.tab_budget = QWidget()
        win.tabs.addTab(win.tab_budget, win.tr_gui("tab_budget"))
        grid = QGridLayout(win.tab_budget)

        # ---------- Filters ----------
        win.gb_budget_filters = QGroupBox()
        win._bind_text(win.gb_budget_filters, "setTitle", "budget_filters_group")
        fbox = win.gb_budget_filters

        fg = QGridLayout(fbox)
        win._budget_filters_grid = fg
        grid.addWidget(fbox, 0, 0, 1, 2)

        # Year + Month filter (explicit)
        win.b_year = QComboBox()
        win.b_month = QComboBox()

        # Year list: current year +/- a few years (or you can populate from CSV later)
        cy = datetime.now().year
        for y in range(cy - 3, cy + 2):
            win.b_year.addItem(str(y))

        # Month list: 1..12
        for m in range(1, 13):
            win.b_month.addItem(f"{m:02d}", m)  # display "01".."12", store int

        win.b_year.setMinimumWidth(90)
        win.b_month.setMinimumWidth(75)

        # --- Default Filters to current year/month ---
        now = datetime.now()
        cy = now.year
        cm = now.month  # 1..12

        # Year combo: set to current year if present
        year_idx = win.b_year.findText(str(cy))
        if year_idx >= 0:
            win.b_year.setCurrentIndex(year_idx)

        # Month combo: items store month int as userData
        month_idx = win.b_month.findData(cm)
        if month_idx >= 0:
            win.b_month.setCurrentIndex(month_idx)

        win.b_apply = QPushButton()
        win._bind_text(win.b_apply, "setText", "budget_apply")

        win.b_clear = QPushButton()
        win._bind_text(win.b_clear, "setText", "budget_clear")

        win.b_apply.setMinimumWidth(100)
        win.b_clear.setMinimumWidth(100)

        win.lbl_budget_year = QLabel()
        win._bind_text(win.lbl_budget_year, "setText", "budget_budget_year")
        win.lbl_budget_month = QLabel()
        win._bind_text(win.lbl_budget_month, "setText", "budget_filter_month")

        win.lbl_budget_year.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        win.lbl_budget_month.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        fg.addWidget(win.lbl_budget_year,  0, 1); fg.addWidget(win.b_year,  0, 2)
        fg.addWidget(win.lbl_budget_month, 0, 3); fg.addWidget(win.b_month, 0, 4)

        fg.addWidget(win.b_apply, 0, 5)
        fg.addWidget(win.b_clear, 0, 6)

        # Make spacing consistent
        fg.setHorizontalSpacing(10)
        fg.setContentsMargins(10, 8, 10, 8)

        # ---------- Inputs: Budget ----------
        win.gb_budget_add = QGroupBox()
        win._bind_text(win.gb_budget_add, "setTitle", "budget_add_group")
        bbox = win.gb_budget_add

        bg = QGridLayout(bbox)
        win._budget_addbudget_grid = bg

        # --- spacing / margins for Add Budget row ---
        bg.setHorizontalSpacing(10)
        bg.setVerticalSpacing(6)
        bg.setContentsMargins(10, 8, 10, 8)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1) 

        win.bt_year = QLineEdit(str(datetime.now().year))
        win.bt_year.setMinimumWidth(90)

        win.bt_cat = QComboBox(); win.bt_cat.setEditable(True)
        win.bt_cat.addItem("", "")

        cat_keys = sorted(win._active_cat_keys(), key=lambda k: (win.cat_label(k) or k).casefold())
        for ck in cat_keys:
            win.bt_cat.addItem(win.cat_label(ck), ck)

        win.bt_amount = QLineEdit()
        win.bt_amount.setValidator(QDoubleValidator(-1e12,1e12,2))
        win.bt_add = QPushButton()
        win._bind_text(win.bt_add, "setText", "budget_budget_add_update")

        # Sizing so the two-column page stays compact
        win.bt_cat.setMinimumContentsLength(14)
        win.bt_amount.setMinimumWidth(120)
        win.bt_add.setMinimumWidth(100)

        # Layout (two rows in this group)
        # Row 0: Month, Category, Amount, Add, Recurring checkbox
        win.lbl_bt_year = QLabel()
        win._bind_text(win.lbl_bt_year, "setText", "budget_budget_year")
        win.lbl_bt_cat = QLabel()
        win._bind_text(win.lbl_bt_cat, "setText", "budget_budget_category")
        win.lbl_bt_amt = QLabel()
        win._bind_text(win.lbl_bt_amt, "setText", "budget_budget_amount")

        win.lbl_bt_year.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        win.lbl_bt_cat.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        win.lbl_bt_amt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        bg.addWidget(win.lbl_bt_year,     0, 1); bg.addWidget(win.bt_year,    0, 2)
        bg.addWidget(win.lbl_bt_cat,      0, 3); bg.addWidget(win.bt_cat,     0, 4)
        bg.addWidget(win.lbl_bt_amt,      0, 5); bg.addWidget(win.bt_amount,  0, 6)
        bg.addWidget(win.bt_add,          0, 7)

        # Place Add Budget block under Filters (full width)
        grid.addWidget(bbox, 1, 0, 1, 2)

        # ---------- Inputs: Income ----------
        win.gb_budget_income = QGroupBox()
        win._bind_text(win.gb_budget_income, "setTitle", "budget_income_group")
        ibox = win.gb_budget_income
        ig = QGridLayout(ibox)

        win._budget_income_grid = ig

        # Place Income block under Add Budget (full width)
        grid.addWidget(ibox, 2, 0, 1, 2)

        # Spacing / margins (match Add Budget)
        ig.setHorizontalSpacing(10)
        ig.setVerticalSpacing(8)
        ig.setContentsMargins(10, 8, 10, 8)

        # ---- Add Income controls (ONE ROW, CENTERED) ----
        win.i_month = QLineEdit()
        win.i_month.setPlaceholderText(win.tr_gui("budget_income_month_placeholder"))
        win.i_month.setToolTip(win.tr_gui("budget_income_month_tooltip"))

        win.i_employer = QLineEdit()
        win.i_biweekly = QLineEdit(); win.i_biweekly.setValidator(QDoubleValidator(-1e12, 1e12, 2))

        win.i_distribs = QComboBox()
        win.i_distribs.addItems(["2", "3"])

        win.i_other = QLineEdit(); win.i_other.setValidator(QDoubleValidator(-1e12, 1e12, 2))

        win.i_add = QPushButton()
        win._bind_text(win.i_add, "setText", "budget_income_add_update")

        win.lbl_im = QLabel()
        win._bind_text(win.lbl_im, "setText", "budget_income_month")
        win.lbl_ie = QLabel()
        win._bind_text(win.lbl_ie, "setText", "budget_income_employer")
        win.lbl_ib = QLabel()
        win._bind_text(win.lbl_ib, "setText", "budget_income_biweekly")
        win.lbl_id = QLabel()
        win._bind_text(win.lbl_id, "setText", "budget_income_dists")
        win.lbl_io = QLabel()
        win._bind_text(win.lbl_io, "setText", "budget_income_other")

        # Align labels right, like Add Budget
        for lbl in (win.lbl_im, win.lbl_ie, win.lbl_ib, win.lbl_id, win.lbl_io):
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Grid row 0: centered by spacers in col 0 and col 12
        ig.addWidget(win.lbl_im,    0, 1); ig.addWidget(win.i_month,    0, 2)
        ig.addWidget(win.lbl_ie,    0, 3); ig.addWidget(win.i_employer, 0, 4)
        ig.addWidget(win.lbl_ib,    0, 5); ig.addWidget(win.i_biweekly, 0, 6)
        ig.addWidget(win.lbl_id,    0, 7); ig.addWidget(win.i_distribs, 0, 8)
        ig.addWidget(win.lbl_io,    0, 9); ig.addWidget(win.i_other,    0, 10)

        ig.addWidget(win.i_add,     0, 11)

        # ---- Income (Combined) label (CENTERED) ----
        win.lbl_income_items = QLabel()
        win._bind_text(win.lbl_income_items, "setText", "budget_income_items_label")
        win.lbl_income_items.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ig.addWidget(win.lbl_income_items, 1, 0, 1, 13)

        # ---- Income (Combined) table (CENTERED, BELOW) ----
        win.tbl_income_combined = QTableView()
        win.tbl_income_combined.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        win.tbl_income_combined.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        win.tbl_income_combined.setAlternatingRowColors(True)
        win.tbl_income_combined.verticalHeader().setVisible(False)

        combined_headers = [
            win.tr_gui("budget_income_month"),
            win.tr_gui("budget_income_header_employer"),
            win.tr_gui("budget_income_header_biweekly"),
            win.tr_gui("budget_income_header_dists"),
            win.tr_gui("budget_income_header_other"),
            win.tr_gui("budget_income_header_month_total"),
            win.tr_gui("budget_income_header_expense_total"),
            win.tr_gui("budget_income_header_variance"),
        ]
        win.model_income_combined = IncomeCombinedModel([], headers=combined_headers)
        win.tbl_income_combined.setModel(win.model_income_combined)

        ch = win.tbl_income_combined.horizontalHeader()
        ch.setStretchLastSection(False)

        # Month + numeric columns: content-sized; Employer: interactive (capped)
        ch.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Month
        ch.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)      # Employer
        for c in range(2, 8):
            ch.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)

        ch.setMinimumSectionSize(60)

        # Baseline widths (tune as desired)
        win.tbl_income_combined.setColumnWidth(0, 90)   # Month
        win.tbl_income_combined.setColumnWidth(1, 180)  # Employer
        win.tbl_income_combined.setColumnWidth(2, 95)   # Bi-weekly
        win.tbl_income_combined.setColumnWidth(3, 60)   # Dists
        win.tbl_income_combined.setColumnWidth(4, 90)   # Other
        win.tbl_income_combined.setColumnWidth(5, 105)  # Month Total
        win.tbl_income_combined.setColumnWidth(6, 115)  # Expense Total
        win.tbl_income_combined.setColumnWidth(7, 95)   # Variance

        # Fixed width so it can truly center
        win.tbl_income_combined.setMinimumWidth(700)
        win.tbl_income_combined.setMaximumWidth(1200)
        win.tbl_income_combined.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        win.tbl_income_combined.setMinimumHeight(70)
        win.tbl_income_combined.setMaximumHeight(140)

        # Center table using an HBox wrapper
        table_wrap = QWidget()
        tw = QHBoxLayout(table_wrap)
        tw.setContentsMargins(0, 0, 0, 0)
        tw.addStretch(1)
        tw.addWidget(win.tbl_income_combined)
        tw.addStretch(1)

        ig.addWidget(table_wrap, 2, 0, 1, 13)

        # ---- Edit/Delete buttons (CENTERED, BELOW TABLE) ----
        btn_wrap = QWidget()
        bw = QHBoxLayout(btn_wrap)
        bw.setContentsMargins(0, 0, 0, 0)
        bw.setSpacing(8)
        bw.addStretch(1)

        win.i_edit = QPushButton()
        win._bind_text(win.i_edit, "setText", "budget_income_edit_selected")
        win.i_delete = QPushButton()
        win._bind_text(win.i_delete, "setText", "budget_income_delete_selected")

        bw.addWidget(win.i_edit)
        bw.addWidget(win.i_delete)

        bw.addStretch(1)
        ig.addWidget(btn_wrap, 3, 0, 1, 13)

        # ---------- Charts ----------
        win.fig_bbar = Figure(figsize=(5, 3), constrained_layout=True)
        win.ax_bbar = win.fig_bbar.add_subplot(111)
        win.canvas_bbar = FigureCanvas(win.fig_bbar)
        win.canvas_bbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        win.lbl_budget_bva_bar = QLabel()
        win._bind_text(win.lbl_budget_bva_bar, "setText", "budget_bva_bar_label")
        grid.addWidget(win.lbl_budget_bva_bar, 5, 0)

        grid.addWidget(win.canvas_bbar,                          6, 0)

        win.fig_bpie = Figure(figsize=(5, 3), constrained_layout=False)
        win.ax_bpie = win.fig_bpie.add_subplot(111)
        win.canvas_bpie = FigureCanvas(win.fig_bpie)
        win.canvas_bpie.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        win.lbl_budget_mix_pie = QLabel()
        win._bind_text(win.lbl_budget_mix_pie, "setText", "budget_mix_pie_label")
        grid.addWidget(win.lbl_budget_mix_pie, 5, 1)

        grid.addWidget(win.canvas_bpie,                          6, 1)

        # Prevent zero-height collapses that trigger constrained_layout warnings
        win.canvas_bbar.setMinimumHeight(240)
        win.canvas_bpie.setMinimumHeight(240)

        # ---------- Budget Breakdown Table (under the pie, right column) ----------
        win.lbl_budget_breakdown = QLabel()
        win._bind_text(win.lbl_budget_breakdown, "setText", "budget_breakdown_label")
        grid.addWidget(win.lbl_budget_breakdown, 7, 1)

        win.tbl_bud = QTableView()
        win.model_bud = SimpleTableModel(
            [win.tr_gui("reports_header_category"), win.tr_gui("budget_bva_header_budget")],
            []
        )

        win.tbl_bud.setModel(win.model_bud)
        win.tbl_bud.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        win.tbl_bud.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        grid.addWidget(win.tbl_bud,                                8, 1)

        # ---------- Budget vs Actual Table (under the bar, left column) ----------
        win.lbl_budget_bva_table = QLabel()
        win._bind_text(win.lbl_budget_bva_table, "setText", "budget_bva_table_label")
        grid.addWidget(win.lbl_budget_bva_table, 7, 0)

        win.tbl_bva = QTableView()
        bva_headers = [
            win.tr_gui("budget_bva_header_category"),
            win.tr_gui("budget_bva_header_budget"),
            win.tr_gui("budget_bva_header_actual"),
            win.tr_gui("budget_bva_header_variance"),
        ]
        win.model_bva = BudgetVsActualModel([], headers=bva_headers)
        win.tbl_bva.setModel(win.model_bva)
        win.tbl_bva.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, 4):
            win.tbl_bva.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        grid.addWidget(win.tbl_bva,                                8, 0)

        # Layout stretch
        grid.setRowStretch(2, 1)  # Income group
        grid.setRowStretch(6, 3)  # charts row
        grid.setRowStretch(8, 4)  # bottom tables row
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Wire up
        win.b_apply.clicked.connect(lambda: apply_budget_filters(win))
        win.b_clear.clicked.connect(lambda: clear_budget_filters(win))
        win.bt_add.clicked.connect(lambda: add_budget_item(win))
        win.i_add.clicked.connect(lambda: add_income_item(win))
        win.i_edit.clicked.connect(lambda: edit_income_selected(win))
        win.i_delete.clicked.connect(lambda: delete_income_selected(win))

def tune_budget_layout(win) -> None:
        narrow = getattr(win, "_ui_bp_narrow", False)
        very_narrow = getattr(win, "_ui_bp_very_narrow", False)

     # -------- Budget Filters row --------
        if hasattr(win, "_budget_filters_grid"):
            fg = win._budget_filters_grid
            # keep buttons compact; allow the center cluster to breathe
            if very_narrow:
                fg.setColumnStretch(0, 0)  # reduce spacer dominance on tiny screens
                fg.setColumnStretch(7, 0)
            else:
                fg.setColumnStretch(0, 1)
                fg.setColumnStretch(7, 1)

        # -------- Add Budget row --------
        if hasattr(win, "_budget_addbudget_grid"):
            bg = win._budget_addbudget_grid

            # Category: elastic but capped
            win.bt_cat.setMinimumWidth(220)
            win.bt_cat.setMaximumWidth(340)
            win.bt_cat.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

            # Column index where bt_cat is placed (from your grid): col 4
            if very_narrow:
                bg.setColumnStretch(4, 2)
            elif narrow:
                bg.setColumnStretch(4, 2)
            else:
                bg.setColumnStretch(4, 2)

            # Reduce spacer dominance on narrow screens
            bg.setColumnStretch(0, 0 if very_narrow else 1)
            bg.setColumnStretch(8, 0 if very_narrow else 1)

        # -------- Add Income row --------
        if hasattr(win, "_budget_income_grid"):
            ig = win._budget_income_grid

            # Employer should always be the elastic field
            win.i_employer.setMinimumWidth(180)
            win.i_employer.setMaximumWidth(360)   # cap it (was effectively unlimited)
            win.i_employer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            # Employer field is col 4
            if very_narrow:
                ig.setColumnStretch(4, 2)  # employer dominates
            elif narrow:
                ig.setColumnStretch(4, 2)
            else:
                ig.setColumnStretch(4, 2)

            # Reduce spacer dominance on narrow screens
            ig.setColumnStretch(0, 0 if very_narrow else 1)
            ig.setColumnStretch(12, 0 if very_narrow else 1)

            # Income table width policy: allow it to shrink on small screens
            if hasattr(win, "tbl_income_combined"):
                if very_narrow:
                    win.tbl_income_combined.setMinimumWidth(600)
                elif narrow:
                    win.tbl_income_combined.setMinimumWidth(650)
                else:
                    win.tbl_income_combined.setMinimumWidth(700)

# === BUDGET: HELPERS ===
def set_budget_filters_to_current(win) -> None:
        now = datetime.now()
        cy, cm = now.year, now.month

        # Year
        y_idx = win.b_year.findText(str(cy))
        if y_idx >= 0:
            win.b_year.setCurrentIndex(y_idx)

        # Month uses userData ints (1..12)
        m_idx = win.b_month.findData(cm)
        if m_idx >= 0:
            win.b_month.setCurrentIndex(m_idx)

def edit_income_selected(win) -> None:
        if not hasattr(win, "tbl_income_combined"):
            return

        sel = win.tbl_income_combined.selectionModel().selectedRows()
        if len(sel) != 1:
            QMessageBox.information(win, win.tr_gui("dlg_info_title"), win.tr_gui("msg_income_select_one"))
            return

        row = sel[0].row()
        month, emp, biw, dists, other = win.model_income_combined.rowValues(row)

        win.i_month.setText(month)
        win.i_employer.setText(emp)
        win.i_biweekly.setText(str(biw))
        win.i_distribs.setCurrentText(str(dists))
        win.i_other.setText(str(other))

        win.i_employer.setFocus()

def delete_income_selected(win) -> None:
        if not hasattr(win, "tbl_income_combined"):
            return

        sel = win.tbl_income_combined.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(win, win.tr_gui("dlg_info_title"), win.tr_gui("msg_income_delete_select"))
            return

        if QMessageBox.question(
            win,
            win.tr_gui("dlg_confirm_delete_title"),
            win.tr_gui("msg_confirm_delete_income_body").format(count=len(sel)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        targets = set()
        for sidx in sel:
            targets.add(win.model_income_combined.rowKey(sidx.row()))  # (month, employer)

        li = win.settings.income_items or []
        li = [it for it in li if (it.get("month", ""), it.get("employer", "")) not in targets]

        win.settings.income_items = li
        save_settings(win.settings)

        apply_budget_filters(win)

def add_income_item(win):
        # Normalize the month. Strictly accepts YYYY-MM; blank uses selected Budget year/month.
        raw_month = (win.i_month.text() or "").strip()
        if not raw_month:
            by = int(win.b_year.currentText())
            bm = int(win.b_month.currentData() or win.b_month.currentText())
            raw_month = f"{by}-{bm:02d}"

        nm = _normalize_month_input_to_ym(raw_month)
        if not nm:
            QMessageBox.warning(
                win,
                win.tr_gui("dlg_info_title"),
                win.tr_gui("msg_month_adjusted").format(raw=raw_month, normalized="YYYY-MM"),
            )
            return
        m = nm

        emp = (win.i_employer.text() or "").strip()
        if not emp:
            QMessageBox.critical(
                win,
                win.tr_gui("dlg_error_title"),
                win.tr_gui("msg_income_employer_required"),
            )
            return

        try:
            biw = float(win.i_biweekly.text() or "0")
        except Exception:
            QMessageBox.critical(
                win,
                win.tr_gui("dlg_error_title"),
                win.tr_gui("msg_income_biweekly_nan"),
            )
            return
        dists = int(win.i_distribs.currentText() or "2")
        try:
            other = float(win.i_other.text() or "0")
        except Exception:
            QMessageBox.critical(
                win,
                win.tr_gui("dlg_error_title"),
                win.tr_gui("msg_income_other_nan"),
            )
            return

        item = IncomeItem(m, emp, biw, dists, other)
        li = win.settings.income_items or []
        # upsert by (month, employer)
        found = False
        for i, it in enumerate(li):
            if it.get("month")==m and it.get("employer")==emp:
                li[i] = asdict(item); found = True; break
        if not found:
            li.append(asdict(item))
        win.settings.income_items = li
        save_settings(win.settings)
        QMessageBox.information(win, win.tr_gui("dlg_info_title"), win.tr_gui("msg_income_saved"))
        apply_budget_filters(win)

def add_budget_item(win):
        cat_label = (win.bt_cat.currentText() or "").strip()
        if not cat_label:
            QMessageBox.critical(win, win.tr_gui("dlg_error_title"), win.tr_gui("msg_choose_category"))
            return

        cat_key = win._combo_key(win.bt_cat, "cat") or cat_label

        # Year
        year_raw = (win.bt_year.text() or "").strip()
        if not (len(year_raw) == 4 and year_raw.isdigit()):
            QMessageBox.critical(
                win,
                win.tr_gui("dlg_error_title"),
                win.tr_gui("msg_budget_year_invalid").format(raw=year_raw),
            )
            return
        year_str = year_raw

        # Amount
        try:
            amt = float(win.bt_amount.text() or "0")
        except Exception:
            QMessageBox.critical(win, win.tr_gui("dlg_error_title"), win.tr_gui("msg_amount_must_be_number"))
            return

        annual = win.settings.annual_budgets or {}
        year_map = annual.get(year_str, {}) or {}
        existing = year_map.get(cat_key, None)

        # Confirm if changing an existing annual amount (affects all months)
        if existing is not None and float(existing) != float(amt):
            msg = win.tr_gui("msg_confirm_budget_template_update").format(
                year=year_str,
                category=win.cat_label(cat_key),
                old=f"{float(existing):,.2f}",
                new=f"{float(amt):,.2f}",
            )
            resp = QMessageBox.question(
                win,
                win.tr_gui("dlg_confirm_title"),
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if resp != QMessageBox.StandardButton.Yes:
                return

        # Save
        year_map[cat_key] = float(amt)
        annual[year_str] = year_map
        win.settings.annual_budgets = annual
        save_settings(win.settings)

        QMessageBox.information(
            win,
            win.tr_gui("dlg_info_title"),
            win.tr_gui("msg_budget_template_saved").format(year=year_str),
        )

        # Refresh budget tab view
        apply_budget_filters(win)

def clear_budget_filters(win) -> None:
        set_budget_filters_to_current(win)
        apply_budget_filters(win)

def apply_budget_filters(win) -> None:
        refresh_budget_tab(win)

def compute_actuals_by_category(win, year: int, month: int) -> Dict[str, float]:
        """Sum actual expenses by category for a specific year+month."""
        src: ExpenseTableModel = win.model
        actuals: Dict[str, float] = {}

        for r in range(src.rowCount()):
            row = src.rows[r]
            amt = parse_amount(row[0])
            if amt is None:
                continue

            d = (row[4] or "").strip()  # 'YYYY-MM-DD'
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
            except Exception:
                continue

            if dt.year != year or dt.month != month:
                continue

            cat_key = row[1]
            actuals[cat_key] = actuals.get(cat_key, 0.0) + amt

        return actuals

def ensure_annual_budget_exists_for_year(win, year: int) -> bool:
        annual = win.settings.annual_budgets or {}
        y = str(year)

        # 1) If we already have ANY budgets saved (any year), do not prompt.
        #    Just ensure the year container exists.
        if annual:
            if y not in annual:
                annual[y] = {}
                win.settings.annual_budgets = annual
                save_settings(win.settings)
            return True

        # 2) If budgets are EMPTY, prompt user to create the first year.
        resp = QMessageBox.question(
            win,
            win.tr_gui("dlg_info_title"),
            win.tr_gui("msg_prompt_create_budget_template").format(year=y),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return False

        annual[y] = {}
        win.settings.annual_budgets = annual
        save_settings(win.settings)
        return True

def refresh_budget_tab(win) -> None:
        # Use user-editable taxonomy labels (settings.taxonomy).
        # `cat_label` will fallback to key if label missing.
        def _cat_label_for_sort(k):
            return (win.cat_label(k) or k).lower()

        budget_year = int(win.b_year.currentText())

        mdata = win.b_month.currentData()
        mnum = int(mdata) if mdata else int(win.b_month.currentText())  # 1..12
        if not (1 <= mnum <= 12):
            return

        target_ym = f"{budget_year}-{mnum:02d}"

        ok = ensure_annual_budget_exists_for_year(win, budget_year)
        if not ok:
            # User declined creating an annual budget. Render charts/tables in "no budget" state.
            win.model_bva.setRows([])
            win.model_bud.setRows([(win.tr_gui("label_no_budget"), 0.0), (win.tr_gui("label_total"), 0.0)])
            win.ax_bbar.clear()
            win.ax_bbar.text(0.5, 0.5, win.tr_gui("chart_no_budget"), ha="center", va="center",
                            transform=win.ax_bbar.transAxes)
            win.canvas_bbar.draw_idle()
            win.ax_bpie.clear()
            win.ax_bpie.text(0.5, 0.5, win.tr_gui("chart_no_budget"), ha="center", va="center",
                            transform=win.ax_bpie.transAxes)
            win.canvas_bpie.draw_idle()
            return

        # ---- Income table rows ----
        actuals = compute_actuals_by_category(win, budget_year, mnum)
        total_expenses = sum(actuals.values())

        income_rows: List[Tuple[str, str, float, int, float, float, float, float]] = []

        for it in (win.settings.income_items or []):
            ik = (it.get("month", "") or "").strip()
            if ik != target_ym:
                continue

            biw   = float(it.get("biweekly_amount", 0.0))
            d     = int(it.get("distributions", 0))
            other = float(it.get("other_income", 0.0))

            month_total = biw * d + other
            variance = month_total - total_expenses

            income_rows.append((
                ik,
                it.get("employer", "Employer"),
                biw,
                d,
                other,
                month_total,
                total_expenses,
                variance
            ))

        win.model_income_combined.setRows(income_rows)

        # Post-load sizing cap for Employer (optional but recommended)
        if hasattr(win, "tbl_income_combined"):
            win.tbl_income_combined.resizeColumnsToContents()

            emp_col = 1
            max_emp = 260
            min_emp = 170
            current = win.tbl_income_combined.columnWidth(emp_col)
            win.tbl_income_combined.setColumnWidth(emp_col, max(min(current, max_emp), min_emp))

        # ---- Budget vs Actual rows ----
        # Annual budget template for the selected budget year
        annual = win.settings.annual_budgets or {}
        year_map = annual.get(str(budget_year), {}) or {}

        budget_by_cat: Dict[str, float] = {}
        for c, v in year_map.items():
            try:
                budget_by_cat[c] = float(v)
            except Exception:
                budget_by_cat[c] = 0.0

        all_cats = set(budget_by_cat.keys()) | set(actuals.keys())

        rows_bva: List[Tuple[str, float, float]] = []
        for c in sorted(all_cats, key=lambda x: _cat_label_for_sort(x)):
            rows_bva.append((win.cat_label(c), budget_by_cat.get(c, 0.0), actuals.get(c, 0.0)))
        win.model_bva.setRows(rows_bva)

        # ---- Budget Breakdown (right-side table) ----
        rows_budget_only = [(win.cat_label(c), v) for c, v in budget_by_cat.items()]
        rows_budget_only.sort(key=lambda t: (t[0] or "").lower())
        total_budget = sum(v for _, v in rows_budget_only)
        rows_budget_only += [(win.tr_gui("label_total"), total_budget)]
        win.model_bud.setRows(rows_budget_only)

        # --- Bar chart: grouped Budget vs Actual ---
        win.ax_bbar.clear()
        if rows_bva:
            labels = [r[0] for r in rows_bva]
            budgets = [r[1] for r in rows_bva]
            actuals_vals = [r[2] for r in rows_bva]
            x = list(range(len(labels)))
            width = 0.4
            b1 = win.ax_bbar.bar([i - width/2 for i in x], budgets, width)
            b2 = win.ax_bbar.bar([i + width/2 for i in x], actuals_vals, width)
            win.ax_bbar.set_xticks(x)
            win.ax_bbar.set_xticklabels(labels, rotation=30, ha="right")
            win.ax_bbar.set_ylabel(win.tr_gui("chart_y_amount"))
            win.ax_bbar.ticklabel_format(style="plain", axis="y")

            # Legend ABOVE, outside the plot area (single call)
            win.ax_bbar.legend(
                [b1, b2], ["Budget", "Actual"],
                loc="lower center",
                bbox_to_anchor=(0.5, 1.02),   # push outside, just above axes
                ncol=2,
                frameon=False
            )
        else:
            win.ax_bbar.text(
                0.5, 0.5,
                win.tr_gui("chart_no_data"),
                ha="center",
                va="center",
                transform=win.ax_bbar.transAxes,
            )
        win.canvas_bbar.draw_idle()

        # --- Pie: Budget mix only ---
        win.ax_bpie.clear()
        if rows_bva:
            labels = [r[0] for r in rows_bva]
            budgets = [max(0.0, r[1]) for r in rows_bva]
            if sum(budgets) > 0:
                wedges, _ = win.ax_bpie.pie(budgets, labels=None, startangle=90)
                win.ax_bpie.axis("equal")

                legend_labels = [f"{lbl} – {v/sum(budgets)*100:.1f}%" for lbl, v in zip(labels, budgets)]
                win._layout_pie_with_legend(win.fig_bpie, win.ax_bpie, wedges, legend_labels)
            else:
                win.ax_bpie.text(
                    0.5, 0.5,
                    win.tr_gui("chart_no_budget"),
                    ha="center",
                    va="center",
                    transform=win.ax_bpie.transAxes,
                )
        else:
            win.ax_bpie.text(
                0.5, 0.5,
                win.tr_gui("chart_no_data"),
                ha="center",
                va="center",
                transform=win.ax_bpie.transAxes,
            )
        win.canvas_bpie.draw_idle()