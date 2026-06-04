# Expense Tracker PyQt

A tested desktop personal finance app built with Python, PyQt6, CSV persistence, budgeting, reporting, and English/Spanish localization.

---

## Features

### Browse Expenses

* View expenses in a sortable table
* Filter by:

  * Name
  * Year
  * Month
  * Category
  * Subcategory
  * Description
* Inline editing
* Delete selected rows
* Multi-row deletion
* Right-click context menu
* Quick Add entry form
* Running totals for filtered data

### Reports

* Expense totals by category
* Expense totals by subcategory
* Category bar chart
* Category pie chart
* Independent report filters
* Top-category reporting

### Budgeting

* Annual budget templates
* Monthly actual spending calculations
* Budget vs Actual reporting
* Variance tracking
* Monthly income tracking
* Budget breakdown tables
* Budget visualizations

### Category Management

* Add categories
* Edit categories
* Archive categories
* Restore archived categories
* Add/Edit/Archive/Restore subcategories
* Fully user-managed taxonomy

### Language Support

* English
* Spanish
* Runtime language switching
* Persistent language preference

### CSV Storage

* Human-readable CSV format
* Atomic writes
* Automatic backup creation
* Header detection in multiple languages
* CSV formula injection protection

---

## CSV Format

The application stores expenses using six columns:

| Column      | Description                    |
| ----------- | ------------------------------ |
| Amount      | Expense amount                 |
| Category    | Category key                   |
| Subcategory | Subcategory key                |
| Description | Expense description            |
| Date        | YYYY-MM-DD                     |
| Name        | Person associated with expense |

---

## Installation

### Clone Repository

```bash
git clone https://github.com/msalas03/expense-tracker-pyqt.git
cd expense-tracker-pyqt
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install PyQt6 matplotlib platformdirs pytest pytest-qt
```

---

## Running

```bash
python expense_tracker_gui.py
```

---

## Running Tests

Execute the full test suite:

```bash
python -m pytest -v
```

Current coverage includes:

* CSV operations
* Quick Add workflows
* Browse filtering
* Reports aggregation
* Budget calculations
* Income tracking
* Row editing
* Row deletion
* Language switching
* Taxonomy persistence
* Settings persistence
* Dialog initialization
* GUI workflows

Current test suite:

```text
73 passing tests
```

---

## Project Structure

```text
expense_tracker/
│
├── gui/
│   ├── dialogs.py
│   └── tabs/
│
├── i18n/
│   └── translations.py
│
├── models/
│
├── services/
│
├── tests/
│
└── expense_tracker_gui.py
```

---

## Roadmap

Planned enhancements:

* Additional Manage Categories dialog testing
* Chart-specific testing
* Responsive layout testing
* Enhanced reporting
* Additional export options
* Package refactoring
* Installer generation

---

## Packaging

Build a standalone executable:

```bash
pyinstaller --name "Expense Tracker" --onefile --windowed --noconfirm expense_tracker_gui.py
```

---

## License

MIT License
