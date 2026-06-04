from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import List, Tuple
import uuid

from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from expense_tracker.models.settings import save_settings

class EditRowDialog(QDialog):
    """Quick editor for a row's editable fields: Amount, Description, Date, Name."""
    def __init__(self, parent, row_data: List[str], tr_gui):
        super().__init__(parent)
        self.tr_gui = tr_gui
        self.setWindowTitle(self.tr_gui("dlg_edit_title"))
        self.setModal(True)
        form = QFormLayout(self)

        # Fields
        self.e_amount = QLineEdit(row_data[0])
        self.e_desc   = QLineEdit(row_data[3])
        self.e_date   = QLineEdit(row_data[4])
        self.e_name   = QLineEdit(row_data[5])

        # Validators
        self.e_amount.setValidator(QDoubleValidator(bottom=-1e12, top=1e12, decimals=2))
        date_regex = QRegularExpression(r"^\d{4}-\d{2}-\d{2}$")
        self.e_date.setValidator(QRegularExpressionValidator(date_regex))

        form.addRow(self.tr_gui("dlg_edit_amount"), self.e_amount)
        form.addRow(self.tr_gui("dlg_edit_description"), self.e_desc)
        form.addRow(self.tr_gui("dlg_edit_date"), self.e_date)
        form.addRow(self.tr_gui("dlg_edit_name"), self.e_name)

        btns = QHBoxLayout()
        ok = QPushButton(self.tr_gui("btn_ok"))
        cancel = QPushButton(self.tr_gui("btn_cancel"))
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addWidget(cancel)
        form.addRow(btns)

    def values(self) -> Tuple[str, str, str, str]:
        return (
            self.e_amount.text().strip(),
            self.e_desc.text().strip(),
            self.e_date.text().strip(),
            self.e_name.text().strip(),
        )

class ManageTaxonomyDialog(QDialog):
    """
    Soft-edit (add/edit/archive/restore) categories and subcategories in settings.taxonomy.
    Keys are stable; labels are editable per language.
    """
    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)
        self.mw = parent
        self.setWindowTitle(self.mw.tr_gui("dlg_manage_categories_title"))
        self.setModal(True)
        self.resize(900, 520)

        self.tx = deepcopy(self.mw._taxonomy())

        root = QVBoxLayout(self)

        # Top split
        split = QHBoxLayout()
        root.addLayout(split)

        # --- Left: Categories
        left = QVBoxLayout()
        split.addLayout(left, 1)

        left.addWidget(QLabel(self.mw.tr_gui("lbl_categories")))
        self.lst_cat = QListWidget()
        left.addWidget(self.lst_cat, 1)

        cat_btns = QHBoxLayout()
        left.addLayout(cat_btns)
        self.btn_cat_add = QPushButton(self.mw.tr_gui("btn_add"))
        self.btn_cat_edit = QPushButton(self.mw.tr_gui("btn_edit"))
        self.btn_cat_archive = QPushButton(self.mw.tr_gui("btn_archive"))
        self.btn_cat_restore = QPushButton(self.mw.tr_gui("btn_restore"))
        for b in (self.btn_cat_add, self.btn_cat_edit, self.btn_cat_archive, self.btn_cat_restore):
            cat_btns.addWidget(b)

        # --- Right: Subcategories for selected category
        right = QVBoxLayout()
        split.addLayout(right, 1)

        right.addWidget(QLabel(self.mw.tr_gui("lbl_subcategories")))
        self.lst_sub = QListWidget()
        right.addWidget(self.lst_sub, 1)

        sub_btns = QHBoxLayout()
        right.addLayout(sub_btns)
        self.btn_sub_add = QPushButton(self.mw.tr_gui("btn_add"))
        self.btn_sub_edit = QPushButton(self.mw.tr_gui("btn_edit"))
        self.btn_sub_archive = QPushButton(self.mw.tr_gui("btn_archive"))
        self.btn_sub_restore = QPushButton(self.mw.tr_gui("btn_restore"))
        for b in (self.btn_sub_add, self.btn_sub_edit, self.btn_sub_archive, self.btn_sub_restore):
            sub_btns.addWidget(b)

        # Bottom
        bottom = QHBoxLayout()
        root.addLayout(bottom)
        bottom.addStretch(1)
        self.btn_close = QPushButton(self.mw.tr_gui("btn_close"))
        bottom.addWidget(self.btn_close)

        # Signals
        self.btn_close.clicked.connect(self.accept)

        self.lst_cat.currentItemChanged.connect(self._refresh_sub_list)

        self.btn_cat_add.clicked.connect(self._cat_add)
        self.btn_cat_edit.clicked.connect(self._cat_edit)
        self.btn_cat_archive.clicked.connect(self._cat_archive)
        self.btn_cat_restore.clicked.connect(self._cat_restore)

        self.btn_sub_add.clicked.connect(self._sub_add)
        self.btn_sub_edit.clicked.connect(self._sub_edit)
        self.btn_sub_archive.clicked.connect(self._sub_archive)
        self.btn_sub_restore.clicked.connect(self._sub_restore)

        # init
        self._refresh_cat_list()

    # ----- helpers
    def _active_count(self, kind: str) -> int:
        if kind == "cat":
            nodes = (self.tx.get("categories") or {}).values()
        else:
            nodes = (self.tx.get("subcategories") or {}).values()

        n = 0
        for node in nodes:
            if isinstance(node, dict) and node.get("active", True):
                n += 1
        return n

    def _cat_items(self):
        cats = self.tx.get("categories") or {}
        items = []
        for k, node in cats.items():
            if not isinstance(node, dict):
                continue
            lab = node.get(self.mw.lang) or node.get("en") or k
            active = node.get("active", True)
            items.append((lab, k, active))
        items.sort(key=lambda x: (x[0] or x[1]).casefold())
        return items

    def _sub_items(self):
        subs = self.tx.get("subcategories") or {}
        items = []
        for k, node in subs.items():
            if not isinstance(node, dict):
                continue
            lab = node.get(self.mw.lang) or node.get("en") or k
            active = node.get("active", True)
            items.append((lab, k, active))
        items.sort(key=lambda x: (x[0] or x[1]).casefold())
        return items

    def _new_key(self, prefix: str) -> str:
        # stable, collision-resistant enough for local use
        return f"{prefix}_{uuid.uuid4().hex[:10]}"

    def _selected_cat_key(self) -> str:
        it = self.lst_cat.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else ""

    def _selected_sub_key(self) -> str:
        it = self.lst_sub.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else ""

    def _refresh_cat_list(self):
        self.lst_cat.clear()
        for lab, k, active in self._cat_items():
            item = QListWidgetItem(lab)
            item.setData(Qt.ItemDataRole.UserRole, k)
            if not active:
                item.setForeground(Qt.GlobalColor.gray)
                item.setToolTip("Archived — existing expenses only")
            self.lst_cat.addItem(item)

        # keep selection if possible
        if self.lst_cat.count() > 0 and self.lst_cat.currentRow() < 0:
            self.lst_cat.setCurrentRow(0)

    def _refresh_sub_list(self, *_):
        self.lst_sub.clear()
        cat_key = self._selected_cat_key()
        if not cat_key:
            return

        groups = self.tx.get("category_groups") or {}
        sub_keys = (groups.get(cat_key) or [])
        if not isinstance(sub_keys, list):
            sub_keys = []

        subs = self.tx.get("subcategories") or {}
        for sk in sub_keys:
            node = subs.get(sk) or {}
            if not isinstance(node, dict):
                continue
            lab = node.get(self.mw.lang) or node.get("en") or sk
            active = node.get("active", True)
            item = QListWidgetItem(lab)
            item.setData(Qt.ItemDataRole.UserRole, sk)
            if not active:
                item.setForeground(Qt.GlobalColor.gray)
                item.setToolTip("Archived — existing expenses only")
            self.lst_sub.addItem(item)

        if self.lst_sub.count() > 0 and self.lst_sub.currentRow() < 0:
            self.lst_sub.setCurrentRow(0)

    def _input_text(self, prompt: str, initial: str = "") -> str:
        txt, ok = QInputDialog.getText(self, self.mw.tr_gui("dlg_input_title"), prompt, text=initial)
        return txt.strip() if ok else ""

    def _confirm(self, msg: str) -> bool:
        resp = QMessageBox.question(
            self,
            self.mw.tr_gui("dlg_confirm_title"),
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return resp == QMessageBox.StandardButton.Yes

    # ----- Category actions
    def _cat_add(self):
        name_en = self._input_text(self.mw.tr_gui("prompt_new_category"))
        if not name_en:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_name_required"))
            return

        # Prompt for Spanish equivalent (optional). Use same default as English.
        # If translation key for the ES prompt is missing, tr_gui will return the key — that's safe.
        name_es = self._input_text(self.mw.tr_gui("prompt_new_category_es"), initial=name_en)
        if not name_es:
            name_es = name_en

        ck = self._new_key("cat")
        cats = self.tx.setdefault("categories", {})
        cats[ck] = {"en": name_en, "es": name_es, "active": True}

        # ensure group exists
        groups = self.tx.setdefault("category_groups", {})
        groups.setdefault(ck, [])

        self._refresh_cat_list()

        # Auto-select the newly added category
        for i in range(self.lst_cat.count()):
            it = self.lst_cat.item(i)
            if it.data(Qt.ItemDataRole.UserRole) == ck:
                self.lst_cat.setCurrentRow(i)
                break

    def _cat_edit(self):
        ck = self._selected_cat_key()
        if not ck:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_item_first"))
            return

        node = (self.tx.get("categories") or {}).get(ck) or {}
        cur_en = node.get("en") or ""
        new_en = self._input_text(self.mw.tr_gui("prompt_edit_category"), initial=cur_en)
        if not new_en:
            return
        node["en"] = new_en
        # keep ES if it was identical to old EN; otherwise leave as-is
        if (node.get("es") or "") == (cur_en or ""):
            node["es"] = new_en
        self.tx["categories"][ck] = node
        self._refresh_cat_list()

    def _cat_archive(self):
        ck = self._selected_cat_key()
        if not ck:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_item_first"))
            return

        # Guardrail: don't allow archiving the last active category
        node = (self.tx.get("categories") or {}).get(ck) or {}
        if node.get("active", True) and self._active_count("cat") <= 1:
            QMessageBox.information(
                self,
                self.mw.tr_gui("dlg_info_title"),
                self.mw.tr_gui("msg_cannot_archive_last_category"),
            )
            return

        lab = (self.tx.get("categories") or {}).get(ck, {}).get(self.mw.lang) or ck
        if not self._confirm(self.mw.tr_gui("msg_confirm_archive").format(name=lab)):
            return

        self.tx["categories"][ck]["active"] = False
        self._refresh_cat_list()
        self._refresh_sub_list()

    def _cat_restore(self):
        ck = self._selected_cat_key()
        if not ck:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_item_first"))
            return
        lab = (self.tx.get("categories") or {}).get(ck, {}).get(self.mw.lang) or ck
        if not self._confirm(self.mw.tr_gui("msg_confirm_restore").format(name=lab)):
            return
        self.tx["categories"][ck]["active"] = True
        self._refresh_cat_list()

    # ----- Subcategory actions (assigned to selected category)
    def _sub_add(self):
        ck = self._selected_cat_key()
        if not ck:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_category_first"))
            return

        name_en = self._input_text(self.mw.tr_gui("prompt_new_subcategory"))
        if not name_en:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_name_required"))
            return

        # Prompt for Spanish equivalent (optional)
        name_es = self._input_text(self.mw.tr_gui("prompt_new_subcategory_es"), initial=name_en)
        if not name_es:
            name_es = name_en

        sk = self._new_key("sub")
        subs = self.tx.setdefault("subcategories", {})
        subs[sk] = {"en": name_en, "es": name_es, "active": True}

        groups = self.tx.setdefault("category_groups", {})
        groups.setdefault(ck, [])
        if sk not in groups[ck]:
            groups[ck].append(sk)

        self._refresh_sub_list()

        # Auto-select the newly added subcategory
        for i in range(self.lst_sub.count()):
            it = self.lst_sub.item(i)
            if it.data(Qt.ItemDataRole.UserRole) == sk:
                self.lst_sub.setCurrentRow(i)
                break

    def _sub_edit(self):
        sk = self._selected_sub_key()
        if not sk:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_item_first"))
            return

        node = (self.tx.get("subcategories") or {}).get(sk) or {}
        cur_en = node.get("en") or ""
        new_en = self._input_text(self.mw.tr_gui("prompt_edit_subcategory"), initial=cur_en)
        if not new_en:
            return
        node["en"] = new_en
        if (node.get("es") or "") == (cur_en or ""):
            node["es"] = new_en
        self.tx["subcategories"][sk] = node
        self._refresh_sub_list()

    def _sub_archive(self):
        sk = self._selected_sub_key()
        if not sk:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_item_first"))
            return

        # Guardrail: don't allow archiving the last active subcategory
        node = (self.tx.get("subcategories") or {}).get(sk) or {}
        if node.get("active", True) and self._active_count("sub") <= 1:
            QMessageBox.information(
                self,
                self.mw.tr_gui("dlg_info_title"),
                self.mw.tr_gui("msg_cannot_archive_last_subcategory"),
            )
            return

        lab = (self.tx.get("subcategories") or {}).get(sk, {}).get(self.mw.lang) or sk
        if not self._confirm(self.mw.tr_gui("msg_confirm_archive").format(name=lab)):
            return

        self.tx["subcategories"][sk]["active"] = False
        self._refresh_sub_list()

    def _sub_restore(self):
        sk = self._selected_sub_key()
        if not sk:
            QMessageBox.information(self, self.mw.tr_gui("dlg_info_title"), self.mw.tr_gui("msg_select_item_first"))
            return
        lab = (self.tx.get("subcategories") or {}).get(sk, {}).get(self.mw.lang) or sk
        if not self._confirm(self.mw.tr_gui("msg_confirm_restore").format(name=lab)):
            return
        self.tx["subcategories"][sk]["active"] = True
        self._refresh_sub_list()

    def accept(self):
        # persist taxonomy to settings on close
        self.mw.settings.taxonomy = self.tx
        save_settings(self.mw.settings)
        super().accept()