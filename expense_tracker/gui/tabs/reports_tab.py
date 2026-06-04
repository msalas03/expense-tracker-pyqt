from datetime import datetime
from typing import Dict, List
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QLabel, QGridLayout, QGroupBox, QWidget, QLineEdit, QComboBox, QPushButton, QSizePolicy, 
    QHeaderView, QTableView
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from expense_tracker.models.table_models import (
    ExpenseFilterProxy,
    SimpleTableModel,
)
from expense_tracker.i18n.translations import TRANSLATIONS
from expense_tracker.services.parse_service import parse_amount


def build_reports_tab(win) -> None:
        win.tab_reports = QWidget()
        win.tabs.addTab(win.tab_reports, win.tr_gui("tab_reports"))
        grid = QGridLayout(win.tab_reports)

        # ---------------- Filters ----------------
        win.gb_reports_filters = QGroupBox()
        win._bind_text(win.gb_reports_filters, "setTitle", "reports_filters_group")
        filter_box = win.gb_reports_filters

        fg = QGridLayout(filter_box)
        win._reports_filters_grid = fg
        grid.addWidget(filter_box, 0, 0, 1, 2)

        win.r_name = QLineEdit()

        # Year + Month dropdowns (Reports)
        win.r_year = QComboBox()
        win.r_month = QComboBox()

        now = datetime.now()
        cy, cm = now.year, now.month

        for y in range(cy - 3, cy + 2):
            win.r_year.addItem(str(y))

        for m in range(1, 13):
            win.r_month.addItem(f"{m:02d}", m)

        win.r_cat = QComboBox()
        win.r_cat.setEditable(True)

        win.r_sub = QComboBox()
        win.r_sub.setEditable(True)

        # Widths
        win.r_name.setMinimumWidth(140)
        win.r_year.setMinimumWidth(110)
        win.r_month.setMinimumWidth(90)

        # Default to current year/month
        y_idx = win.r_year.findText(str(cy))
        if y_idx >= 0:
            win.r_year.setCurrentIndex(y_idx)

        m_idx = win.r_month.findData(cm)
        if m_idx >= 0:
            win.r_month.setCurrentIndex(m_idx)

        win.r_cat.addItem("", "")
        cat_keys = sorted(win._active_cat_keys(), key=lambda k: (win.cat_label(k) or k).casefold())
        for ck in cat_keys:
            win.r_cat.addItem(win.cat_label(ck), ck)

        win.r_sub.addItem("", "")
        sub_keys = sorted(win._active_sub_keys(), key=lambda k: (win.sub_label(k) or k).casefold())
        for sk in sub_keys:
            win.r_sub.addItem(win.sub_label(sk), sk)

        # Layout
        win.lbl_reports_name = QLabel()
        win._bind_text(win.lbl_reports_name, "setText", "reports_filter_name")
        fg.addWidget(win.lbl_reports_name, 0, 0)

        fg.addWidget(win.r_name, 0, 1)

        win.lbl_reports_year = QLabel()
        win._bind_text(win.lbl_reports_year, "setText", "budget_budget_year")
        fg.addWidget(win.lbl_reports_year, 0, 2)

        fg.addWidget(win.r_year, 0, 3)

        win.lbl_reports_month = QLabel()
        win._bind_text(win.lbl_reports_month, "setText", "budget_filter_month")
        fg.addWidget(win.lbl_reports_month, 0, 4)

        fg.addWidget(win.r_month, 0, 5)

        win.lbl_reports_cat = QLabel()
        win._bind_text(win.lbl_reports_cat, "setText", "reports_filter_category")
        fg.addWidget(win.lbl_reports_cat, 0, 6)

        fg.addWidget(win.r_cat, 0, 7)

        win.lbl_reports_sub = QLabel()
        win._bind_text(win.lbl_reports_sub, "setText", "reports_filter_subcategory")
        fg.addWidget(win.lbl_reports_sub, 0, 8)

        fg.addWidget(win.r_sub, 0, 9)

        win.r_apply = QPushButton()
        win._bind_text(win.r_apply, "setText", "reports_apply")

        win.r_clear = QPushButton()
        win._bind_text(win.r_clear, "setText", "reports_clear")

        fg.addWidget(win.r_apply, 0, 10)
        fg.addWidget(win.r_clear, 0, 11)

        # Dedicated proxy for Reports
        win.report_proxy = ExpenseFilterProxy(win.lang)
        win.report_proxy.setSourceModel(win.model)

        win.r_cat.currentTextChanged.connect(lambda txt: on_report_filter_cat_changed(win, txt))
        win.r_apply.clicked.connect(lambda: apply_report_filters(win))
        win.r_clear.clicked.connect(lambda: clear_report_filters(win))

        # ---------------- Charts (TOP) ----------------
        win.fig_bar = Figure(figsize=(5, 3), tight_layout=True)
        win.ax_bar = win.fig_bar.add_subplot(111)
        win.canvas_bar = FigureCanvas(win.fig_bar)
        win.canvas_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        win.lbl_reports_bar = QLabel()
        win._bind_text(win.lbl_reports_bar, "setText", "reports_top_categories_bar")
        grid.addWidget(win.lbl_reports_bar, 1, 0)

        grid.addWidget(win.canvas_bar, 2, 0)

        win.fig_pie = Figure(figsize=(5, 3), constrained_layout=False)
        win.ax_pie = win.fig_pie.add_subplot(111)
        win.canvas_pie = FigureCanvas(win.fig_pie)
        win.canvas_pie.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        win.lbl_reports_pie = QLabel()
        win._bind_text(win.lbl_reports_pie, "setText", "reports_category_mix_pie")
        grid.addWidget(win.lbl_reports_pie, 1, 1)

        grid.addWidget(win.canvas_pie, 2, 1)

        # ---------------- Tables (BOTTOM) ----------------
        win.tbl_by_cat = QTableView()
        win.model_by_cat = SimpleTableModel(
            [win.tr_gui("reports_header_category"), win.tr_gui("reports_header_total")],
            []
        )
        win.tbl_by_cat.setModel(win.model_by_cat)
        win.tbl_by_cat.horizontalHeader().setStretchLastSection(False)
        win.tbl_by_cat.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        win.tbl_by_cat.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        win.tbl_by_cat.setAlternatingRowColors(True)
        win.lbl_reports_tbl_cat = QLabel()
        win._bind_text(win.lbl_reports_tbl_cat, "setText", "reports_totals_by_category")
        grid.addWidget(win.lbl_reports_tbl_cat, 3, 0)

        grid.addWidget(win.tbl_by_cat, 4, 0)

        win.tbl_by_sub = QTableView()
        win.model_by_sub = SimpleTableModel(
            [win.tr_gui("reports_header_subcategory"), win.tr_gui("reports_header_total")],
            []
        )
        win.tbl_by_sub.setModel(win.model_by_sub)
        win.tbl_by_sub.horizontalHeader().setStretchLastSection(False)
        win.tbl_by_sub.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        win.tbl_by_sub.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        win.tbl_by_sub.setAlternatingRowColors(True)
        win.lbl_reports_tbl_sub = QLabel()
        win._bind_text(win.lbl_reports_tbl_sub, "setText", "reports_totals_by_subcategory")
        grid.addWidget(win.lbl_reports_tbl_sub, 3, 1)

        grid.addWidget(win.tbl_by_sub, 4, 1)

        # Stretching: give charts some height, tables a bit more for rows
        grid.setRowStretch(2, 3)   # charts canvases
        grid.setRowStretch(4, 4)   # tables
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Initial refresh
        apply_report_filters(win)

def tune_reports_layout(win) -> None:
        if not hasattr(win, "_reports_filters_grid"):
            return

        fg = win._reports_filters_grid
        narrow = getattr(win, "_ui_bp_narrow", False)
        very_narrow = getattr(win, "_ui_bp_very_narrow", False)

        # Let these expand; avoid the “combo hogs everything” effect
        win.r_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        win.r_cat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        win.r_sub.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Indices: 1 name, 7 cat, 9 sub (based on addWidget layout in your file)
        if very_narrow:
            fg.setColumnStretch(1, 3)  # name
            fg.setColumnStretch(7, 2)  # cat
            fg.setColumnStretch(9, 2)  # sub
        elif narrow:
            fg.setColumnStretch(1, 2)
            fg.setColumnStretch(7, 2)
            fg.setColumnStretch(9, 2)
        else:
            fg.setColumnStretch(1, 2)
            fg.setColumnStretch(7, 2)
            fg.setColumnStretch(9, 2)

        fg.setColumnStretch(10, 0)  # apply
        fg.setColumnStretch(11, 0)  # clear

def on_report_filter_cat_changed(win, _txt: str = "") -> None:
        """Restrict Subcategory list based on selected Category in Reports filter."""
        prev_sub = win._combo_key(win.r_sub, "sub")
        cat_key = win._combo_key(win.r_cat, "cat")

        win.r_sub.blockSignals(True)
        win.r_sub.clear()
        win.r_sub.addItem("", "")

        if not cat_key:
            sub_keys = sorted(win._active_sub_keys(), key=lambda k: (win.sub_label(k) or k).casefold())
            for sk in sub_keys:
                win.r_sub.addItem(win.sub_label(sk), sk)
        else:
            for sk in win._subs_for_cat(cat_key):
                win.r_sub.addItem(win.sub_label(sk), sk)

        if prev_sub:
            idx = win.r_sub.findData(prev_sub)
            if idx >= 0:
                win.r_sub.setCurrentIndex(idx)

        win.r_sub.blockSignals(False)

def apply_report_filters(win) -> None:
        """Apply Reports filters to the dedicated proxy and refresh outputs."""
        ry = int(win.r_year.currentText())
        mdata = win.r_month.currentData()
        rm = int(mdata) if mdata is not None else 1
        target_ym = f"{ry}-{rm:02d}"

        win.report_proxy.setFilters(
            (win.r_name.text() or "").strip(),
            target_ym,
            win._combo_key(win.r_cat, "cat"),
            win._combo_key(win.r_sub, "sub"),
            "",  # desc not used
        )

        # Defer refresh so the proxy has applied the new filter
        QTimer.singleShot(0, lambda: refresh_reports(win))

def clear_report_filters(win) -> None:
        win.r_name.clear()
        win.r_cat.setCurrentIndex(0)
        win.r_sub.setCurrentIndex(0)

        now = datetime.now()
        cy, cm = now.year, now.month

        y_idx = win.r_year.findText(str(cy))
        if y_idx >= 0:
            win.r_year.setCurrentIndex(y_idx)

        m_idx = win.r_month.findData(cm)
        if m_idx >= 0:
            win.r_month.setCurrentIndex(m_idx)

        apply_report_filters(win)

def compute_reports_data(win) -> None:
        """Return (by_cat_labeled, by_sub_labeled_full) using the Reports proxy-visible subset."""
        src = win.model
        if not src.rows:
            return [], []

        # Canonical way: iterate proxy rows and map to source rows
        filtered: List[List[str]] = []
        for pr in range(win.report_proxy.rowCount()):
            src_index = win.report_proxy.mapToSource(win.report_proxy.index(pr, 0))
            if src_index.isValid():
                filtered.append(src.rows[src_index.row()])

        if not filtered:
            return [], []

        cat_labels = TRANSLATIONS[win.lang]["categories"]
        sub_labels = TRANSLATIONS[win.lang]["subcategories"]

        by_cat: Dict[str, float] = {}
        by_sub: Dict[str, float] = {}

        for row in filtered:
            amt = parse_amount(row[0])
            if amt is None:
                continue
            ckey, skey = row[1], row[2]
            by_cat[ckey] = by_cat.get(ckey, 0.0) + amt
            by_sub[skey] = by_sub.get(skey, 0.0) + amt

        # Use current taxonomy labels (fallback to key)
        by_cat_labeled = [(win.cat_label(k), v) for k, v in by_cat.items()]
        by_sub_labeled_full = [(win.sub_label(k), v) for k, v in by_sub.items()]

        by_cat_labeled.sort(key=lambda t: t[1], reverse=True)
        by_sub_labeled_full.sort(key=lambda t: t[1], reverse=True)

        return by_cat_labeled, by_sub_labeled_full

def refresh_reports(win) -> None:
        """Recompute tables and redraw charts."""
        by_cat, by_sub_full = compute_reports_data(win)
        no_data = win.tr_gui("label_no_data")

        label_total = win.tr_gui("label_total")
        total_cat = sum(v for _l, v in by_cat)
        total_sub = sum(v for _l, v in by_sub_full)

        # Display only top 20 subcategories, but total from full list
        by_sub_display = by_sub_full[:20]

        rows_cat = by_cat + [(label_total, total_cat)]
        rows_sub = by_sub_display + [(label_total, total_sub)]

        # Update tables (use rows with totals)
        win.model_by_cat.setRows(rows_cat)
        win.model_by_sub.setRows(rows_sub)

        # --- Bar: top categories (up to 10 for clarity) [NO LABELS]
        win.ax_bar.clear()
        top_bar = by_cat[:10]
        labels = [l for (l, _v) in top_bar]
        values = [v for (_l, v) in top_bar]
        if values:
            bars = win.ax_bar.bar(range(len(values)), values)
            win.ax_bar.set_xticks(range(len(labels)))
            win.ax_bar.set_xticklabels(labels, rotation=30, ha="right")
            win.ax_bar.set_ylabel(win.tr_gui("chart_y_total"))
            win.ax_bar.ticklabel_format(style="plain", axis="y")
        else:
            win.ax_bar.text(0.5, 0.5, no_data, ha="center", va="center",
                            transform=win.ax_bar.transAxes)
        win.canvas_bar.draw_idle()

        # --- Pie: category mix (legend instead of labels)
        win.ax_pie.clear()
        if by_cat:
            labels_p = [l for (l, _v) in by_cat]
            values_p = [v for (_l, v) in by_cat]
            total = sum(values_p) if values_p else 0.0

            wedges, _ = win.ax_pie.pie(values_p, labels=None, startangle=90)
            win.ax_pie.axis("equal")

            # Build legend entries with percentages
            if total != 0:
                legend_labels = [f"{lbl} – {v/total*100:.1f}%" for lbl, v in zip(labels_p, values_p)]
            else:
                legend_labels = labels_p

            win._layout_pie_with_legend(win.fig_pie, win.ax_pie, wedges, legend_labels)
        else:
            win.ax_pie.text(0.5, 0.5, no_data, ha="center", va="center", transform=win.ax_pie.transAxes)

        win.canvas_pie.draw_idle()