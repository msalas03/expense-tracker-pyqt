from datetime import datetime
from PyQt6.QtCore import (
    Qt, QModelIndex, QDate
)
from PyQt6.QtWidgets import (
    QLabel, QGridLayout, QGroupBox, QWidget, QLineEdit, QComboBox, QPushButton, QSizePolicy, 
    QHeaderView, QTableView, QVBoxLayout, QHBoxLayout, QDateEdit
)
from matplotlib.figure import Figure
from expense_tracker.models.table_models import (
    ExpenseTableModel,
    ExpenseFilterProxy,
)


def build_browse_tab(win, headers) -> None:
        win.tab_browse = QWidget()
        win.tabs.addTab(win.tab_browse, win.tr_gui("tab_browse"))

        layout = QVBoxLayout(win.tab_browse)

        # Filters row
        win.gb_browse_filters = QGroupBox()
        win._bind_text(win.gb_browse_filters, "setTitle", "browse_filters_group")
        filter_box = win.gb_browse_filters

        grid = QGridLayout(filter_box)
        win._browse_filters_grid = grid
        layout.addWidget(filter_box)

        win.f_name = QLineEdit()

        # Year + Month dropdowns (Browse)
        win.f_year = QComboBox()
        win.f_month = QComboBox()   
        # Category / Subcategory combobox values depend on user taxonomy (settings)
        win.f_cat = QComboBox(); win.f_cat.setEditable(True)
        win.f_sub = QComboBox(); win.f_sub.setEditable(True)

        # Populate Year + Month dropdowns (Browse defaults to current year/month)
        now = datetime.now()
        cy, cm = now.year, now.month

        for y in range(cy - 3, cy + 2):
            win.f_year.addItem(str(y))

        for m in range(1, 13):
            win.f_month.addItem(f"{m:02d}", m)  # display "01".."12", store int

        # Default to current year/month
        y_idx = win.f_year.findText(str(cy))
        if y_idx >= 0:
            win.f_year.setCurrentIndex(y_idx)

        m_idx = win.f_month.findData(cm)
        if m_idx >= 0:
            win.f_month.setCurrentIndex(m_idx)

        # Populate taxonomy-driven combos (store keys in userData)
        win.f_cat.addItem("", "")
        cat_keys = sorted(win._active_cat_keys(), key=lambda k: (win.cat_label(k) or k).casefold())
        for ck in cat_keys:
            win.f_cat.addItem(win.cat_label(ck), ck)

        win.f_sub.addItem("", "")
        sub_keys = sorted(win._active_sub_keys(), key=lambda k: (win.sub_label(k) or k).casefold())
        for sk in sub_keys:
            win.f_sub.addItem(win.sub_label(sk), sk)

        win.lbl_browse_name = QLabel()
        win._bind_text(win.lbl_browse_name, "setText", "browse_filter_name")
        grid.addWidget(win.lbl_browse_name, 0, 0)
        grid.addWidget(win.f_name, 0, 1)

        # Year + Month
        win.lbl_browse_year = QLabel()
        win._bind_text(win.lbl_browse_year, "setText", "budget_budget_year")
        grid.addWidget(win.lbl_browse_year, 0, 2)
        grid.addWidget(win.f_year, 0, 3)

        win.lbl_browse_month = QLabel()
        win._bind_text(win.lbl_browse_month, "setText", "browse_filter_month")
        grid.addWidget(win.lbl_browse_month, 0, 4)
        grid.addWidget(win.f_month, 0, 5)

        win.lbl_browse_cat = QLabel()
        win._bind_text(win.lbl_browse_cat, "setText", "browse_filter_category")
        grid.addWidget(win.lbl_browse_cat, 0, 6)
        grid.addWidget(win.f_cat, 0, 7)

        win.lbl_browse_sub = QLabel()
        win._bind_text(win.lbl_browse_sub, "setText", "browse_filter_subcategory")
        grid.addWidget(win.lbl_browse_sub, 0, 8)
        grid.addWidget(win.f_sub, 0, 9)

        # Description filter
        win.f_desc = QLineEdit()
        win.lbl_browse_desc = QLabel()
        win._bind_text(win.lbl_browse_desc, "setText", "browse_filter_desc")
        grid.addWidget(win.lbl_browse_desc, 0, 10)
        grid.addWidget(win.f_desc, 0, 11)

        win.btn_apply = QPushButton()
        win._bind_text(win.btn_apply, "setText", "browse_apply_filters")

        win.btn_clear = QPushButton()
        win._bind_text(win.btn_clear, "setText", "browse_clear_filters")

        grid.addWidget(win.btn_apply, 0, 12)
        grid.addWidget(win.btn_clear, 0, 13)

        # Table
        # Pass a resolver so the model can render human-friendly labels for category/subcategory.
        win.model = ExpenseTableModel(
            headers,
            [],
            label_resolver=lambda col, raw: (win.cat_label(raw) if col == 1 else (win.sub_label(raw) if col == 2 else raw))
        )

        win.proxy = ExpenseFilterProxy(win.lang)
        win.proxy.setSourceModel(win.model)

        win.table = QTableView()
        win.table.setModel(win.proxy)
        win.table.setSortingEnabled(True)
        win.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        win.table.setAlternatingRowColors(True)
        layout.addWidget(win.table, stretch=1)

        # --- Column sizing ---
        header = win.table.horizontalHeader()
        header.setStretchLastSection(False)  # we'll manage stretch explicitly
        # 0 Amount, 1 Category, 2 Subcategory, 3 Description, 4 Date, 5 Name
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Amount compact
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Category compact
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Subcat compact
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Description flexes
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Date compact
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)       # Name fixed but resizable
        win.table.setColumnWidth(5, 110)                                        # Keep Name from hogging space

        # --- Row actions ---
        row_actions = QHBoxLayout()
        win.btn_edit = QPushButton()
        win._bind_text(win.btn_edit, "setText", "browse_edit_selected")
        win.btn_delete = QPushButton()
        win._bind_text(win.btn_delete, "setText", "browse_delete_selected")

        row_actions.addStretch(1)
        row_actions.addWidget(win.btn_edit)
        row_actions.addWidget(win.btn_delete)
        layout.addLayout(row_actions)

        # Connectors
        win.btn_edit.clicked.connect(win._edit_selected)
        win.btn_delete.clicked.connect(win._delete_selected)

        # Save on inline edits
        win.model.dataChanged.connect(lambda *_: win._save_model())

        # Right-click context menu
        win.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        win.table.customContextMenuRequested.connect(win._table_context_menu)

        # Quick Add strip
        qa = QGroupBox()
        win._bind_text(qa, "setTitle", "browse_quick_group")
        gl = QGridLayout(qa)
        win._browse_quickadd_grid = gl
        layout.addWidget(qa)

        win.qa_amount = QLineEdit()
        win.qa_cat = QComboBox(); win.qa_sub = QComboBox()
        win.qa_cat.clear()
        cat_keys = sorted(win._active_cat_keys(), key=lambda k: (win.cat_label(k) or k).casefold())
        for ck in cat_keys:
            win.qa_cat.addItem(win.cat_label(ck), ck)

        # sub list will refresh on cat change
        win.qa_date = QDateEdit()
        win.qa_date.setCalendarPopup(True)
        win.qa_date.setDisplayFormat("yyyy-MM-dd")
        win.qa_date.setDate(QDate.currentDate())
        win.qa_desc = QLineEdit()
        win.qa_name = QLineEdit(win.settings.username)
        win.qa_add_btn = QPushButton()
        win._bind_text(win.qa_add_btn, "setText", "browse_quick_add_button")

        win.lbl_qa_amount = QLabel()
        win._bind_text(win.lbl_qa_amount, "setText", "browse_quick_amount")
        gl.addWidget(win.lbl_qa_amount, 0, 0)
        gl.addWidget(win.qa_amount, 0, 1)
        win.lbl_qa_cat = QLabel()
        win._bind_text(win.lbl_qa_cat, "setText", "browse_quick_category")
        gl.addWidget(win.lbl_qa_cat, 0, 2)
        gl.addWidget(win.qa_cat, 0, 3)
        win.lbl_qa_sub = QLabel()
        win._bind_text(win.lbl_qa_sub, "setText", "browse_quick_subcategory")
        gl.addWidget(win.lbl_qa_sub, 0, 4)
        gl.addWidget(win.qa_sub, 0, 5)

        # Date label + widget (Quick Add)
        win.lbl_qa_date = QLabel()
        win._bind_text(win.lbl_qa_date, "setText", "browse_quick_date")
        gl.addWidget(win.lbl_qa_date, 0, 6)
        gl.addWidget(win.qa_date, 0, 7)

        # Description label and field
        win.lbl_qa_desc = QLabel()
        win._bind_text(win.lbl_qa_desc, "setText", "browse_quick_desc")
        gl.addWidget(win.lbl_qa_desc, 0, 8)
        gl.addWidget(win.qa_desc, 0, 9)

        # Name field in the grid
        win.lbl_qa_name = QLabel()
        win._bind_text(win.lbl_qa_name, "setText", "browse_quick_name")
        gl.addWidget(win.lbl_qa_name, 0, 10)
        gl.addWidget(win.qa_name, 0, 11)
        # Add button
        gl.addWidget(win.qa_add_btn, 0, 12)

        # Connectors
        win.btn_apply.clicked.connect(lambda: apply_filters(win))
        win.btn_clear.clicked.connect(lambda: clear_filters(win))
        win.f_cat.currentTextChanged.connect(lambda txt: on_filter_cat_changed(win, txt))
        win.qa_cat.currentTextChanged.connect(lambda txt: refresh_qa_subs(win))
        win.qa_add_btn.clicked.connect(win._quick_add)

        # Seed sub list
        refresh_qa_subs(win)

        # Start with Amount sorted descending
        win.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        tune_browse_layout(win)

def tune_browse_layout(win) -> None:
        """Responsive tuning for Browse tab Filters + Quick Add."""
        if not hasattr(win, "_browse_filters_grid") or not hasattr(win, "_browse_quickadd_grid"):
            return

        # Use central widget width; fallback to window width
        w = win.centralWidget().width() if win.centralWidget() else win.width()

        narrow = w < 1050
        very_narrow = w < 920

        # --------------------
        # Filters row tuning
        # --------------------
        fg = win._browse_filters_grid

        # Ensure key fields can expand
        win.f_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        win.f_desc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Combos expand but shouldn't dominate
        win.f_cat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        win.f_sub.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Column indices in your grid (based on addWidget calls):
        # 1=Name field, 7=Category field, 9=Subcategory field, 11=Desc field
        if very_narrow:
            fg.setColumnStretch(1, 1)    # Name (reduced)
            fg.setColumnStretch(7, 2)    # Category
            fg.setColumnStretch(9, 3)    # Subcategory (increased)
            fg.setColumnStretch(11, 6)   # Desc
        elif narrow:
            fg.setColumnStretch(1, 1)    # Name (reduced)
            fg.setColumnStretch(7, 2)    # Category
            fg.setColumnStretch(9, 3)    # Subcategory (increased)
            fg.setColumnStretch(11, 5)   # Desc
        else:
            fg.setColumnStretch(1, 1)    # Name (reduced)
            fg.setColumnStretch(7, 2)    # Category
            fg.setColumnStretch(9, 3)    # Subcategory (increased)
            fg.setColumnStretch(11, 4)   # Desc

        # Buttons should not stretch
        fg.setColumnStretch(12, 0)
        fg.setColumnStretch(13, 0)

        # --------------------
        # Quick Add row tuning
        # --------------------
        qg = win._browse_quickadd_grid

        win.qa_desc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Name should be stable (not collapsing), but also not consuming all space
        win.qa_name.setMinimumWidth(140)
        win.qa_name.setMaximumWidth(220)
        win.qa_name.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # Column indices in your Quick Add grid:
        # 3=Category field, 5=Subcat field, 9=Desc field, 11=Name field
        if very_narrow:
            qg.setColumnStretch(3, 2)
            qg.setColumnStretch(5, 3)
            qg.setColumnStretch(9, 6)    # Desc dominates
            qg.setColumnStretch(11, 1)   # Name minimal
        elif narrow:
            qg.setColumnStretch(3, 2)
            qg.setColumnStretch(5, 3)
            qg.setColumnStretch(9, 5)
            qg.setColumnStretch(11, 2)
        else:
            qg.setColumnStretch(3, 2)
            qg.setColumnStretch(5, 3)
            qg.setColumnStretch(9, 4)
            qg.setColumnStretch(11, 2)

        qg.setColumnStretch(12, 0)  # Add button

# ---- Filters ----
def apply_filters(win):
    fy = int(win.f_year.currentText())
    mdata = win.f_month.currentData()
    fm = int(mdata) if mdata is not None else 1
    target_ym = f"{fy}-{fm:02d}"

    win.proxy.setFilters(
        (win.f_name.text() or "").strip(),
        target_ym,
        win._combo_key(win.f_cat, "cat"),
        win._combo_key(win.f_sub, "sub"),
        (win.f_desc.text() or "").strip(),
    )

    win._update_status()

def clear_filters(win):
        win.f_name.clear()
        now = datetime.now()
        cy, cm = now.year, now.month

        y_idx = win.f_year.findText(str(cy))
        if y_idx >= 0:
            win.f_year.setCurrentIndex(y_idx)

        m_idx = win.f_month.findData(cm)
        if m_idx >= 0:
            win.f_month.setCurrentIndex(m_idx)

        win.f_cat.setCurrentIndex(0)
        win.f_sub.setCurrentIndex(0)
        win.f_desc.clear() 
        apply_filters(win)

def on_filter_cat_changed(win, _txt=""):
        # If category changes, restrict sub list
        prev_sub = win._combo_key(win.f_sub, "sub")
        cat_key = win._combo_key(win.f_cat, "cat")

        win.f_sub.blockSignals(True)
        win.f_sub.clear()
        win.f_sub.addItem("", "")

        if not cat_key:
            # Show all active subcategories
            sub_keys = sorted(win._active_sub_keys(), key=lambda k: (win.sub_label(k) or k).casefold())
            for sk in sub_keys:
                win.f_sub.addItem(win.sub_label(sk), sk)
        else:
            for sk in win._subs_for_cat(cat_key):
                win.f_sub.addItem(win.sub_label(sk), sk)

        # restore previous selection if still valid
        if prev_sub:
            idx = win.f_sub.findData(prev_sub)
            if idx >= 0:
                win.f_sub.setCurrentIndex(idx)

        win.f_sub.blockSignals(False)

# ---- Quick Add ----
def refresh_qa_subs(win):
        cat_key = win._combo_key(win.qa_cat, "cat")
        win.qa_sub.blockSignals(True)
        win.qa_sub.clear()

        for sk in win._subs_for_cat(cat_key) if cat_key else []:
            win.qa_sub.addItem(win.sub_label(sk), sk)

        win.qa_sub.blockSignals(False)