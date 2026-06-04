from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import (
    Qt,
    QAbstractTableModel,
    QModelIndex,
    QVariant,
    QSortFilterProxyModel,
    QTimer,
)

from PyQt6.QtGui import QColor, QFont

from expense_tracker.services.parse_service import parse_amount

class ExpenseTableModel(QAbstractTableModel):
    """Backed by a list of 6-element rows: [Amount, Category, Subcategory, Description, Date, Name]."""

    def __init__(
        self,
        headers: List[str],
        rows: List[List[str]] | None = None,
        label_resolver: callable | None = None,  # new optional callable: (col_index:int, raw_value:str) -> display_label:str
    ):
        super().__init__()
        self.headers = headers[:6]
        self.rows: List[List[str]] = rows or []
        # callable used to convert stored keys (cat/sub keys) into display labels.
        # signature: label_resolver(col_index, raw_value) -> str
        self.label_resolver = label_resolver

    # --- Core model ---
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return QVariant()
        r, c = index.row(), index.column()
        val = self.rows[r][c] if (0 <= r < len(self.rows) and 0 <= c < 6) else ""
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            # Pretty-print currency for display
            if c == 0 and role == Qt.ItemDataRole.DisplayRole:
                try:
                    x = float(str(val).replace("$", "").replace(",", "").strip())
                    sign = "-" if x < 0 else ""
                    x = abs(x)
                    return f"{sign}${x:,.2f}"
                except Exception:
                    return val

            # For Category (1) and Subcategory (2) display a resolved label if resolver provided,
            # but return the raw value for EditRole (so edits keep raw key semantics if ever enabled).
            if role == Qt.ItemDataRole.DisplayRole and c in (1, 2) and self.label_resolver:
                try:
                    lbl = self.label_resolver(c, val)
                    return lbl if lbl is not None else val
                except Exception:
                    return val

            return val

        # Alignment per column
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if c == 0:
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)   # Amount
            if c == 4:
                return int(Qt.AlignmentFlag.AlignCenter)                                   # Date
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return section + 1

    def flags(self, index: QModelIndex):  # type: ignore[override]
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        base = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        # Allow inline editing for: Amount(0), Description(3), Date(4), Name(5)
        if index.column() in (0, 3, 4, 5):
            base |= Qt.ItemFlag.ItemIsEditable
        return base

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole):  # type: ignore[override]
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False
        r, c = index.row(), index.column()
        if not (0 <= r < len(self.rows)):
            return False

        text = str(value).strip()

        # Validate Amount
        if c == 0:
            try:
                amt = float(str(text).replace("$", "").replace(",", "").strip())
            except Exception:
                return False
            self.rows[r][0] = f"{amt}"
        # Validate Date (YYYY-MM-DD)
        elif c == 4:
            try:
                datetime.strptime(text, "%Y-%m-%d")
            except Exception:
                return False
            self.rows[r][4] = text
        else:
            self.rows[r][c] = text

        self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole, Qt.ItemDataRole.DisplayRole])
        return True

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):  # type: ignore[override]
        reverse = order == Qt.SortOrder.DescendingOrder
        if column == 0:  # Amount numeric
            def keyfn(r):
                try:
                    return float(str(r[0]).replace("$", "").replace(",", "").strip())
                except Exception:
                    return float("-inf")
        elif column == 4:  # Date
            def keyfn(r):
                try:
                    return datetime.strptime(r[4], "%Y-%m-%d")
                except Exception:
                    return datetime.min
        else:
            def keyfn(r):
                return str(r[column]).lower()
        self.layoutAboutToBeChanged.emit()
        self.rows.sort(key=keyfn, reverse=reverse)
        self.layoutChanged.emit()

    def setHeaders(self, headers: list[str]):
        """
        Update model headers (used for live language switching).
        """
        self.headers = headers[:6]
        # notify views that horizontal headers changed
        try:
            self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.headers) - 1)
        except Exception:
            # older Qt versions may behave slightly differently; ignore safely
            pass


class ExpenseFilterProxy(QSortFilterProxyModel):
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang
        self.q_name = ""
        self.q_month = ""
        self.q_cat = ""
        self.q_sub = ""
        self.q_desc = ""
        self._invalidate_scheduled = False 
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def _request_invalidate(self) -> None:
        """Defer filter rebuild to avoid Qt view re-entrancy crashes (macOS especially)."""
        if self._invalidate_scheduled:
            return
        self._invalidate_scheduled = True
        QTimer.singleShot(0, self._do_invalidate)

    def _do_invalidate(self) -> None:
        self._invalidate_scheduled = False
        self.invalidateFilter()

    def setLanguage(self, lang: str):
        self.lang = lang
        self._request_invalidate()

    def setFilters(self, name="", month="", category="", subcategory="", desc=""):
        self.q_name = (name or "").strip().lower()
        self.q_month = (month or "").strip()
        self.q_cat = (category or "").strip().lower()
        self.q_sub = (subcategory or "").strip().lower()
        self.q_desc = (desc or "").strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # type: ignore[override]
        model: ExpenseTableModel = self.sourceModel()  # type: ignore
        r = model.rows[source_row]
        amount, category, subcategory, desc, date_str, name = r

        # --- Name exact match (case-insensitive) ---
        if self.q_name:
            if (name or "").strip().lower() != self.q_name:
                return False

        # --- Date / Month filter (strict YYYY-MM expected in self.q_month) ---
        dt = None
        try:
            dt = datetime.strptime((date_str or "").strip(), "%Y-%m-%d")
        except Exception:
            dt = None

        mq_raw = (self.q_month or "").strip()
        if mq_raw:
            # Require strict 'YYYY-MM'
            if not (len(mq_raw) == 7 and mq_raw[4] == "-"):
                return False
            try:
                qy = int(mq_raw[:4])
                qm = int(mq_raw[5:7])
            except Exception:
                return False
            if not dt or dt.year != qy or dt.month != qm:
                return False

        # --- Category filter (exact on localized label/key as used in model rows) ---
        if self.q_cat:
            if (category or "").strip().lower() != self.q_cat:
                return False

        # --- Subcategory filter (exact) ---
        if self.q_sub:
            if (subcategory or "").strip().lower() != self.q_sub:
                return False

        # --- Description substring match (case-insensitive) ---
        if self.q_desc:
            if self.q_desc not in (desc or "").lower():
                return False

        # Passed all checks
        return True

    # Ensure numeric sort for Amount and chronological sort for Date
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # type: ignore[override]
        src: ExpenseTableModel = self.sourceModel()  # type: ignore
        c = left.column()

        # Defensive: get the backing rows
        try:
            lr = src.rows[left.row()]
            rr = src.rows[right.row()]
        except Exception:
            return super().lessThan(left, right)

        # Amount column (0): sort by numeric value
        if c == 0:
            lv = parse_amount(lr[0])
            rv = parse_amount(rr[0])
            if lv is None: lv = float("-inf")
            if rv is None: rv = float("-inf")
            return lv < rv

        # Date column (4): sort by YYYY-MM-DD date
        if c == 4:
            def to_dt(s: str):
                try:
                    return datetime.strptime(s, "%Y-%m-%d")
                except Exception:
                    return datetime.min
            return to_dt(lr[4]) < to_dt(rr[4])

        # Fallback: case-insensitive string compare
        return str(lr[c]).lower() < str(rr[c]).lower()


class SimpleTableModel(QAbstractTableModel):
    """2-column readonly model: [Label, Amount] for reports tables."""
    def __init__(self, headers: List[str], rows: List[Tuple[str, float]] | None = None):
        super().__init__()
        self.headers = headers[:]
        self.rows: List[Tuple[str, float]] = rows or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent.isValid() else 2

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return QVariant()

        r, c = index.row(), index.column()
        label, amt = self.rows[r]

        # Make last row (grand total) bold
        if role == Qt.ItemDataRole.FontRole and r == len(self.rows) - 1:
            f = QFont()
            f.setBold(True)
            return f

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if c == 0:
                return label
            if c == 1:
                sign = "-" if amt < 0 else ""
                a = abs(amt)
                return f"{sign}${a:,.2f}"

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) if c == 0 \
                else int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return section + 1

    def setRows(self, rows: List[Tuple[str, float]]):
        self.layoutAboutToBeChanged.emit()
        self.rows = rows
        self.layoutChanged.emit()

    def setHeaders(self, headers: List[str]):
        self.headers = headers[:]
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, 1)


# === BUDGET: TABLE MODELS (ANCHOR) ===
class BudgetVsActualModel(QAbstractTableModel):
    """Columns: Category, Budget, Actual, Variance (Actual - Budget)."""
    def __init__(self, 
                 rows: List[Tuple[str, float, float]] | None = None,
                 headers: Optional[List[str]] = None):
        super().__init__()
        self.rows = rows or []  # (category_label, budget, actual)
        self.headers = headers or ["Category", "Budget", "Actual", "Variance"]

    def rowCount(self, parent=QModelIndex()): 
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()): 
        return 4

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): 
            return QVariant()
        r, c = index.row(), index.column()
        label, budget, actual = self.rows[r]
        variance = actual - budget

        # Main display
        if role == Qt.ItemDataRole.DisplayRole:
            if c == 0: return label
            if c == 1: return f"${budget:,.2f}"
            if c == 2: return f"${actual:,.2f}"
            if c == 3:
                sign = "-" if variance < 0 else ""
                return f"{sign}${abs(variance):,.2f}"

        # Align numeric columns right
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) if c == 0 \
                else int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Conditional coloring: green if under budget, red if over
        if role == Qt.ItemDataRole.ForegroundRole and c in (2, 3):
            return QColor(0, 128, 0) if actual <= budget else QColor(178, 34, 34)

        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole: 
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return section + 1

    def setRows(self, rows: List[Tuple[str, float, float]]):
        self.layoutAboutToBeChanged.emit()
        self.rows = rows
        self.layoutChanged.emit()

    def setHeaders(self, headers: List[str]):
        self.headers = headers[:]
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.headers) - 1)


class IncomeCombinedModel(QAbstractTableModel):
    """
    One combined table:
    Columns: Month, Employer, Bi-weekly, Dists, Other, Month Total, Expense Total, Variance
    Rows: (month, employer, biweekly, dists, other, month_total, expense_total, variance)
    """
    def __init__(
        self,
        rows: List[Tuple[str, str, float, int, float, float, float, float]] | None = None,
        headers: Optional[List[str]] = None,
    ):
        super().__init__()
        self.rows = rows or []
        self.headers = headers or [
            "Month", "Employer", "Bi-weekly", "Dists", "Other",
            "Month Total", "Expense Total", "Variance",
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 8

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return QVariant()

        r, c = index.row(), index.column()
        month, employer, biweekly, dists, other, month_total, expense_total, variance = self.rows[r]

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if c == 0:  # Month
                return month
            if c == 1:  # Employer
                return employer
            if c == 2:  # Bi-weekly
                return f"${biweekly:,.2f}"
            if c == 3:  # Dists
                return dists
            if c == 4:  # Other
                return f"${other:,.2f}"
            if c == 5:  # Month Total
                return f"${month_total:,.2f}"
            if c == 6:  # Expense Total
                return f"${expense_total:,.2f}"
            if c == 7:  # Variance
                sign = "-" if variance < 0 else ""
                return f"{sign}${abs(variance):,.2f}"

        if role == Qt.ItemDataRole.TextAlignmentRole:
            # Month/Employer left; numbers right; dists centered
            if c in (0, 1):
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if c == 3:
                return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if role == Qt.ItemDataRole.ForegroundRole and c == 7:
            return QColor(0, 128, 0) if variance >= 0 else QColor(178, 34, 34)

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return section + 1

    def setRows(self, rows: List[Tuple[str, str, float, int, float, float, float, float]]):
        self.layoutAboutToBeChanged.emit()
        self.rows = rows
        self.layoutChanged.emit()

    def rowKey(self, row: int) -> Tuple[str, str]:
        """Return (month, employer) for delete/upsert logic."""
        m, emp, *_ = self.rows[row]
        return (m, emp)

    def rowValues(self, row: int) -> Tuple[str, str, float, int, float]:
        """Return (month, employer, biweekly, dists, other) for edit fill-in."""
        m, emp, biw, d, oth, *_rest = self.rows[row]
        return (m, emp, biw, d, oth)

    def setHeaders(self, headers: List[str]):
        self.headers = headers[:]
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.headers) - 1)
