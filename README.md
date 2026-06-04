# Expense Tracker PyQt

A tested desktop personal finance app built with Python, PyQt6, CSV persistence, budgeting, reporting, and English/Spanish localization.

Expense Tracker PyQt is a desktop personal finance application focused on maintaining the simplicity of CSV-based storage while providing budgeting, reporting, localization, and automated test coverage.

---

## Project Statistics

- 106 automated tests (pytest + pytest-qt)
- PyQt6 desktop GUI
- English / Spanish localization
- Expense tracking and budgeting
- Income management
- Dynamic category taxonomy
- CSV-based persistence
- Matplotlib reporting and visualization

---

## Architecture

The application follows a layered design:

- GUI Layer (PyQt6)
- Services Layer
- Models Layer
- Localization Layer
- CSV Persistence Layer
- Automated Test Layer

This separation keeps business logic independent from the user interface and improves maintainability and testability.

---

## Technologies

- Python 3.13
- PyQt6
- Matplotlib
- pytest
- pytest-qt
- platformdirs
- CSV persistence

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

Current test status:

106 / 106 passing

---

## Quality Assurance

The project currently includes:

- 106 automated tests
- GUI testing with pytest-qt
- CSV persistence validation
- Browse workflow testing
- Reports workflow testing
- Budget workflow testing
- Taxonomy management testing
- Settings persistence testing
- Localization testing
- Error-path and recovery testing

---

## Project Structure

```text
expense_tracker/
│
├── gui/
│   ├── dialogs.py
│   └── tabs/
│       ├── browse_tab.py
│       ├── reports_tab.py
│       ├── budget_tab.py
│       └── help_tab.py
│
├── i18n/
│   └── translations.py
│
├── models/
│   ├── settings.py
│   └── table_models.py
│
├── services/
│   ├── csv_service.py
│   └── parse_service.py
│
├── tests/
|   ├── test_browse_workflows.py
|   ├── test_budget_workflows.py
|   ├── test_csv_workflows.py
|   ├── test_gui_core.py
|   ├── test_reports_workflows.py
|   └── conftest.py
│
├── expense_tracker_gui.py
├── requirements.txt
└── pytest.ini
```

---

## Development

Run tests:

```bash
python -m pytest -v
```

---

## Roadmap

Planned enhancements:

- Additional integration testing
- Sample data package
- Dashboard export capabilities
- Advanced reporting options
- Packaging and installer improvements
- Project restructuring into a distributable package
- Enhanced budgeting analytics
- Screenshot documentation

---

## Screenshots

Screenshots will be added in a future release.

Planned screenshots:

- Browse Tab
- Reports Tab
- Budget Tab
- Manage Categories Dialog

---

## Sample Data

A sample dataset will be provided in a future release to allow users to explore the application without creating their own expense file.

---

## Packaging

Build a standalone Windows executable:

```bash
pyinstaller --name "Expense Tracker" --onefile --windowed --noconfirm expense_tracker_gui.py
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Disclaimer

This software is intended for educational and personal use. It is not financial, tax, accounting, or investment advice. Users are responsible for validating all financial information and calculations.