# translations.py
# Central translations for Expense Tracker GUI (EN / ES)

TRANSLATIONS = {
    "en": {
        # --- CSV + data model structure (used by GUI core) ---
        "csv_headers": ["Amount", "Category", "Subcategory", "Description", "Date", "Name"],
        "categories": {
            "housing": "Housing",
            "food": "Food",
            "transport": "Transport",
            "personal": "Personal",
            "lifestyle": "Lifestyle",
            "work": "Work",
            "finance": "Finance",
            "other": "Other",
        },
        "subcategories": {
            "rent": "Rent",
            "mortgage": "Mortgage",
            "utilities": "Utilities",
            "insurance": "Insurance",
            "groceries": "Groceries",
            "restaurants": "Restaurants",
            "delivery": "Delivery",
            "fuel": "Fuel",
            "public_transport": "Public Transport",
            "private_transport": "Private Transport",
            "car_maintenance": "Car Maintenance",
            "parking": "Parking",
            "clothing": "Clothing",
            "healthcare": "Healthcare",
            "gym": "Gym",
            "personal_care": "Personal Care",
            "jupiter": "Jupiter",
            "entertainment": "Entertainment",
            "travel": "Travel",
            "gaming": "Gaming",
            "events": "Events",
            "education": "Education",
            "certifications": "Certifications",
            "work_supplies": "Work Supplies",
            "subscriptions": "Subscriptions",
            "loan_payment_principal": "Loan Payment (Principal)",
            "loan_interest": "Loan Interest",
            "investment_contribution": "Investment Contribution",
            "savings_contribution": "Savings Contribution",
            "debt_payment": "Debt Payment",
            "brokerage_fees": "Brokerage Fees",
            "bank_fees": "Bank Fees",
            "gifts": "Gifts",
            "donations": "Donations",
            "misc": "Misc",
        },
        "category_groups": {
            "housing": ["rent", "mortgage", "utilities", "insurance"],
            "food": ["groceries", "restaurants", "delivery"],
            "transport": ["fuel", "public_transport", "private_transport", "car_maintenance", "parking"],
            "personal": ["clothing", "healthcare", "gym", "personal_care", "jupiter"],
            "lifestyle": ["entertainment", "travel", "gaming", "events"],
            "work": ["education", "certifications", "work_supplies", "subscriptions"],
            "finance": [
                "loan_payment_principal",
                "loan_interest",
                "investment_contribution",
                "savings_contribution",
                "debt_payment",
                "brokerage_fees",
                "bank_fees",
            ],
            "other": ["gifts", "donations", "misc"],
        },

        # --- GUI strings ---
        "gui": {
            # Tabs
            "tab_browse": "Browse",
            "tab_reports": "Reports",
            "tab_budget": "Budget",
            "tab_help": "Help",

            # Browse tab: Filters
            "browse_filters_group": "Filters",
            "browse_filter_name": "Name:",
            "browse_filter_month": "Month:",
            "browse_filter_category": "Category:",
            "browse_filter_subcategory": "Subcategory:",
            "browse_filter_desc": "Desc:",
            "browse_apply_filters": "Apply Filters",
            "browse_clear_filters": "Clear",

            # Browse tab: Table
            "browse_edit_selected": "Edit Selected",
            "browse_delete_selected": "Delete Selected",

            # Browse tab: Quick Add
            "browse_quick_group": "Quick Add",
            "browse_quick_amount": "Amount",
            "browse_quick_category": "Category",
            "browse_quick_subcategory": "Subcategory",
            "browse_quick_date": "Date",
            "browse_quick_desc": "Desc",
            "browse_quick_name": "Name",
            "browse_quick_add_button": "Add",

            # Reports tab: Filters & labels
            "reports_filters_group": "Filters",
            "reports_filter_name": "Name:",
            "reports_filter_month": "Month:",
            "reports_filter_category": "Category:",
            "reports_filter_subcategory": "Subcategory:",
            "reports_apply": "Apply",
            "reports_clear": "Clear",
            "reports_top_categories_bar": "Top Categories (Bar)",
            "reports_category_mix_pie": "Category Mix (Pie)",
            "reports_totals_by_category": "Totals by Category",
            "reports_totals_by_subcategory": "Totals by Subcategory (Top 20)",

            # Reports tab: Table headers (used via SimpleTableModel headers)
            "reports_header_category": "Category",
            "reports_header_subcategory": "Subcategory",
            "reports_header_total": "Total",

            # Budget tab: Filters
            "budget_filters_group": "Filters",
            "budget_filter_month": "Month:",
            "budget_apply": "Apply",
            "budget_clear": "Clear",

            # Budget tab: Income group
            "budget_income_group": "Add Income",
            "budget_income_month": "Month",
            "budget_income_month_placeholder": "YYYY-MM",
            "budget_income_employer": "Employer",
            "budget_income_biweekly": "Bi-weekly",
            "budget_income_dists": "Dists",
            "budget_income_other": "Other",
            "budget_income_add_update": "Add/Update",

            # Budget tab: Budget group
            "budget_budget_month": "Month",
            "budget_budget_category": "Category",
            "budget_budget_amount": "Amount",
            "budget_budget_add_update": "Add/Update",
            "budget_add_group": "Add Budget (Year Template)",
            "msg_prompt_create_budget_template": "No budget template exists yet. Create a budget template for {year} now?",
            "msg_budget_template_saved": "Budget template saved for {year}.",
            "msg_confirm_budget_template_update": (
                "You are updating the monthly budget template amount for {category} in {year}.\n\n"
                "Old monthly amount: ${old}\n"
                "New monthly amount: ${new}\n\n"
                "This monthly amount will be used for every month in {year}."
            ),
            "help_budget_template_note": (
                "Budgets are stored as a year template: one monthly amount per category for the selected year."
            ),

            # Budget tab: Summary / charts / tables labels
            "budget_income_summary_label": "Income Summary",
            "budget_bva_bar_label": "Budget vs Actual (Bar)",
            "budget_bva_table_label": "Budget vs Actual",
            "budget_breakdown_label": "Budget Breakdown",
            "budget_mix_pie_label": "Budget Mix (Pie)",

            # Budget tab: IncomeSummaryModel headers
            "budget_income_header_employer": "Employer",
            "budget_income_header_biweekly": "Bi-weekly",
            "budget_income_header_dists": "Dists",
            "budget_income_header_other": "Other",
            "budget_income_header_month_total": "Month Total",
            "budget_income_header_expense_total": "Expense Total",
            "budget_income_header_variance": "Variance",

            # Budget tab: BudgetVsActualModel headers
            "budget_bva_header_category": "Category",
            "budget_bva_header_budget": "Budget",
            "budget_bva_header_actual": "Actual",
            "budget_bva_header_variance": "Variance",

            # Menus
            "menu_file": "File",
            "menu_file_new_csv": "New CSV",
            "menu_file_open_csv": "Open CSV",
            "menu_file_exit": "Exit",
            "menu_actions": "Actions",
            "menu_actions_totals": "Totals",
            "menu_help": "Help",
            "menu_help_item": "Help",
            "menu_language": "Language",
            "menu_language_english": "English",
            "menu_language_spanish": "Spanish",
            "msg_language_changed_restart": "Language updated. Restart the app to ensure all labels update everywhere.",

            # Dialog titles
            "dlg_new_csv_title": "New expense CSV",
            "dlg_open_csv_title": "Open expense CSV",
            "dlg_error_title": "Error",
            "dlg_info_title": "Info",
            "dlg_totals_title": "Totals",
            "dlg_confirm_delete_title": "Confirm Delete",
            "dlg_confirm_exit_title": "Confirm Exit",
            "msg_csv_loaded_empty": "The CSV file was opened, but no rows could be parsed. The file may be malformed or use unexpected headers.",

            # Dialog / message bodies
            "msg_location_not_writable": "Selected location is not writable.",
            "msg_no_csv_open": "Please open or create a CSV first.",
            "msg_invalid_amount": "Amount must be a number, e.g., 12.34 or (12.34).",
            "msg_invalid_date": "Date must be YYYY-MM-DD.",
            "msg_invalid_cat_sub": "Choose a valid category/subcategory pair.",
            "msg_expense_saved": "Expense added.",
            "msg_edit_select_one": "Select exactly one row to edit.",
            "msg_delete_select": "Select one or more rows to delete.",
            "msg_confirm_delete_body": "Delete {count} selected row(s)? This cannot be undone.",
            "msg_totals_none": "No expenses match the current filters.",
            "msg_close_confirm_body": "Are you sure you want to close Expense Tracker?",
            "msg_month_adjusted": "Interpreted '{raw}' as '{normalized}'. Use YYYY-MM or a month like '2'/'Feb'.",
            "budget_budget_year": "Year",
            "budget_income_items_label": "Income Items",
            "budget_income_edit_selected": "Edit Selected",
            "budget_income_delete_selected": "Delete Selected",
            "dlg_confirm_title": "Confirm",
            "msg_income_select_one": "Select exactly one income row to edit.",
            "msg_income_delete_select": "Select one or more income rows to delete.",
            "msg_confirm_delete_income_body": "Delete {count} selected income row(s)? This cannot be undone.",
            "msg_income_saved": "Income saved.",
            "msg_budget_year_invalid": "Year must be a 4-digit number (got '{raw}').",
            "menu_manage_categories": "Manage Categories…",
            "dlg_manage_categories_title": "Manage Categories",
            "lbl_categories": "Categories",
            "lbl_subcategories": "Subcategories",
            "btn_add": "Add",
            "btn_edit": "Edit",
            "btn_archive": "Archive",
            "btn_restore": "Restore",
            "btn_close": "Close",
            "lbl_label_en": "Label (English)",
            "lbl_label_es": "Label (Spanish)",
            "msg_select_category_first": "Select a category first.",
            "msg_select_item_first": "Select an item first.",
            "msg_name_required": "Please enter a name.",
            "msg_confirm_archive": "Archive '{name}'? Existing expenses will remain unchanged.",
            "msg_confirm_restore": "Restore '{name}'?",
            "dlg_input_title": "Input",
            "prompt_new_category": "New category name (English):",
            "prompt_new_subcategory": "New subcategory name (English):",
            "prompt_edit_category": "Edit category name (English):",
            "prompt_edit_subcategory": "Edit subcategory name (English):",
            "menu_tools": "Tools",
            "msg_cannot_archive_last_category": "You can’t archive the last active category.",
            "msg_cannot_archive_last_subcategory": "You can’t archive the last active subcategory.",
            "prompt_new_category_es": "Spanish label for the new category (optional)",
            "prompt_new_subcategory_es": "Spanish label for the new subcategory (optional)",

            # Generic labels used in tables/charts
            "label_total": "Total",
            "label_overall_total": "Overall Total",
            "label_no_data": "No data",
            "label_no_budget": "No budget",

            # Status bar
            "status_rows_total": "{rows} rows • ${total:.2f} total",

            # App title
            "app_title": "Expense Tracker",

            # File / CSV / save errors
            "msg_csv_not_writable": "CSV is not writable.",
            "msg_save_failed": "Failed to save: {error}",

            # Income / Budget validation
            "msg_income_biweekly_nan": "Bi-weekly must be a number.",
            "msg_income_other_nan": "Other must be a number.",
            "msg_choose_category": "Choose a Category.",
            "msg_amount_must_be_number": "Amount must be a number.",
            "msg_income_employer_required": "Employer is required.",

            # Edit dialog + buttons
            "dlg_edit_title": "Edit Expense",
            "dlg_edit_amount": "Amount",
            "dlg_edit_description": "Description",
            "dlg_edit_date": "Date (YYYY-MM-DD)",
            "dlg_edit_name": "Name",
            "btn_ok": "OK",
            "btn_cancel": "Cancel",

            # Income month tooltip
            "budget_income_month_tooltip": "Enter YYYY-MM (example: 2026-01)",

            # Help
            "help_title": "Expense Tracker — Help & Guide",

            # Help HTML
            "help_html": """
            <html>
            <head>
                <style>
                    body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
                    h1, h2, h3 { margin: 0.6em 0 0.3em; }
                    h1 { font-size: 18px; }
                    h2 { font-size: 16px; }
                    h3 { font-size: 14px; }
                    p, li { line-height: 1.35; }
                    code, kbd { background:#f5f5f5; padding:2px 4px; border-radius:4px; }
                    .box { border:1px solid #ddd; border-radius:6px; padding:12px; background:#fafafa; }
                    .toc a { text-decoration:none; }
                    .def-table { border-collapse: collapse; width: 100%; }
                    .def-table th, .def-table td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
                    .def-table th { background:#f7f7f7; text-align:left; }
                    .tip { background:#eef9f1; border:1px solid #c9ecd6; padding:8px; border-radius:6px; }
                    .warn { background:#fff7e6; border:1px solid #ffe0a3; padding:8px; border-radius:6px; }
                </style>
            </head>
            <body>
                <div class="box toc">
                    <strong>Table of Contents</strong>
                    <ol>
                        <li><a href="#getting-started">Getting Started</a></li>
                        <li><a href="#browse">Browse Tab</a></li>
                        <li><a href="#reports">Reports Tab</a></li>
                        <li><a href="#budget">Budget Tab</a></li>
                        <li><a href="#definitions">Definitions (Glossary)</a></li>
                        <li><a href="#shortcuts">Keyboard Shortcuts</a></li>
                        <li><a href="#troubleshooting">Troubleshooting</a></li>
                    </ol>
                </div>

                <h1 id="getting-started">Getting Started</h1>
                <p>
                    Use <strong>File → New CSV</strong> to create a new expense file (with headers),
                    or <strong>File → Open CSV</strong> to open an existing one. The status bar at the
                    bottom shows the <em>visible rows</em> and their <em>total</em> after filters.
                </p>
                <p class="tip"><strong>Tip:</strong> Amounts can be typed as <code>12.34</code> or <code>(12.34)</code> for negatives.</p>

                <h2 id="manage-categories">Manage Categories &amp; Subcategories</h2>
                <p>You can add, edit, archive, or restore categories and subcategories used throughout the app.</p>
                <ol>
                    <li>Go to <b>Tools → Manage Categories</b>.</li>
                    <li>Select a category to view its subcategories.</li>
                    <li>Use <b>Add</b>, <b>Edit</b>, <b>Archive</b>, or <b>Restore</b>.</li>
                </ol>
                <ul>
                    <li><b>Archive</b> hides the item from dropdowns but keeps existing expenses/budgets readable.</li>
                    <li>If an item is still used, it can remain visible in reports/tables for historical data, but will not appear for new entry.</li>
                </ul>

                <h1 id="browse">Browse Tab</h1>
                <h3>Filters</h3>
                <ul>
                    <li><strong>Name</strong> — exact match on the Name column.</li>
                    <li><strong>Month</strong> — accepts <code>1</code>, <code>Jan</code>, <code>January</code> (English/Spanish supported).</li>
                    <li><strong>Category/Subcategory</strong> — pick from the lists (translated labels supported).</li>
                    <li><strong>Desc</strong> — case-insensitive substring match of Description.</li>
                </ul>
                <p>
                    Click <strong>Apply Filters</strong> to filter; <strong>Clear</strong> resets all.
                    Right-click the table for <em>Edit</em> or <em>Delete</em>. Select a row and press
                    <strong>Edit Selected</strong> to change Amount, Description, Date, or Name.
                </p>

                <h3>Quick Add</h3>
                <ul>
                    <li>Enter <strong>Amount</strong>, pick a valid <strong>Category/Subcategory</strong> pair, set <strong>Date</strong>, optionally add <strong>Desc</strong> and <strong>Name</strong>.</li>
                    <li>Click <strong>Add</strong>. Data is saved to the open CSV immediately.</li>
                </ul>
                <p class="warn"><strong>Note:</strong> Category/Subcategory must be a valid pair or the add will be rejected.</p>

                <h1 id="reports">Reports Tab</h1>
                <p>
                    Reports have their own filters (separate from Browse). The <strong>Bar</strong> shows top categories,
                    and the <strong>Pie</strong> shows category mix (legend displays percentages).
                </p>
                <ul>
                    <li><strong>Totals by Category/Subcategory</strong> tables include a final <em>Total</em> row in bold.</li>
                </ul>

                <h1 id="budget">Budget Tab</h1>
                <h3>Filters</h3>
                <p>
                    Use the <strong>Year</strong> and <strong>Month</strong> dropdowns to focus the Budget view.
                    The selection affects <strong>Actual</strong> expenses and income calculations for that specific year/month.
                </p>
                <p class="tip">
                    <strong>Tip:</strong> Income entries are matched by <code>YYYY-MM</code> (for example, <code>2026-01</code>), so the same month number in different years is treated separately.
                </p>

                <h3>Add Income</h3>
                <ul>
                    <li><strong>Month</strong> (accepts <code>YYYY-MM</code>, <code>YYYY-MM-DD</code>, or a month like <code>3</code>/<code>Mar</code>), <strong>Employer</strong>, <strong>Bi-weekly</strong> amount, number of <strong>Dists</strong> (2 or 3), and any <strong>Other</strong> income.</li>
                    <li>Click <strong>Add/Update</strong> to upsert by (<em>month</em>, <em>employer</em>).</li>
                </ul>

                <h3>Add Budget (Year Template)</h3>
                    <ul>
                        <li>Enter a <strong>Year</strong>, choose a <strong>Category</strong>, and enter an <strong>Amount</strong>, then click <strong>Add/Update</strong>.</li>
                        <li>This amount is treated as a <strong>monthly budget template</strong> for that category in the selected year.</li>
                        <li>The Budget vs Actual view compares the selected month’s <strong>Actual</strong> expenses against that year’s saved <strong>monthly template</strong> amounts.</li>
                    </ul>

                <h3>Income Summary (top strip)</h3>
                <ul>
                    <li><strong>Month Total</strong> — computed as <em>Bi-weekly × Dists + Other</em>.</li>
                    <li><strong>Expense Total</strong> — sum of all actual expenses for the selected month.</li>
                    <li><strong>Variance</strong> — <em>Month Total − Expense Total</em> (green if ≥ 0, red if &lt; 0).</li>
                </ul>

                <h3>Budget vs Actual</h3>
                <ul>
                    <li>Left table shows <em>Budget</em>, <em>Actual</em>, and <em>Variance</em> per category (Actual ≤ Budget in green, otherwise red).</li>
                    <li>Bar chart compares Budget vs Actual; legend is shown above the plot area.</li>
                    <li>Right table lists <em>Budget Breakdown</em> with a final <em>Total</em> row.</li>
                    <li>Pie shows the <em>Budget Mix</em>.</li>
                </ul>

                <h1 id="definitions">Definitions (Glossary)</h1>
                <table class="def-table">
                    <tr><th>Term</th><th>Meaning</th></tr>
                    <tr><td><strong>Amount</strong></td><td>The transaction value. Negatives can be entered as <code>(12.34)</code>.</td></tr>
                    <tr><td><strong>Category / Subcategory</strong></td><td>Classification keys used for reporting and budgets.</td></tr>
                    <tr><td><strong>Month</strong></td><td>Filter accepts numeric or named months (<em>Jan</em>/<em>Enero</em>, etc.).</td></tr>
                    <tr><td><strong>Budget</strong></td><td>The planned <strong>monthly</strong> spend per category stored as a template for the selected <strong>year</strong>.</td></tr>             
                    <tr><td><strong>Actual</strong></td><td>The sum of real expenses recorded for that category/month.</td></tr>
                    <tr>
                        <td><strong>Variance</strong></td>
                        <td>
                            <ul style="margin:0; padding-left:18px;">
                                <li><strong>Budget vs Actual:</strong> <em>Actual − Budget</em> (green when Actual ≤ Budget; red when Actual &gt; Budget).</li>
                                <li><strong>Income Summary:</strong> <em>Month Total − Expense Total</em> (green when ≥ 0; red when &lt; 0).</li>
                            </ul>
                        </td>
                    </tr>
                    <tr><td><strong>Distributions (Dists)</strong></td><td>The count of bi-weekly pay periods in the month (2 or 3).</td></tr>
                    <tr><td><strong>Other (Income)</strong></td><td>Any monthly income that isn’t in the bi-weekly paycheck (e.g., bonuses, side income).</td></tr>
                </table>

                <h1 id="shortcuts">Keyboard Shortcuts</h1>
                <ul>
                    <li><strong>Ctrl+N</strong> — New CSV</li>
                    <li><strong>Ctrl+O</strong> — Open CSV</li>
                    <li><strong>Ctrl+T</strong> — Totals popup (Browse)</li>
                    <li><strong>F1</strong> — Open Help tab</li>
                </ul>

                <h1 id="troubleshooting">Troubleshooting</h1>
                <ul>
                    <li><strong>I can’t save:</strong> Ensure the CSV location is writable.</li>
                    <li><strong>Categories don’t match:</strong> Pick a valid Category/Subcategory pair from the lists.</li>
                    <li><strong>Dates rejected:</strong> Use <code>YYYY-MM-DD</code>.</li>
                    <li><strong>Totals look off:</strong> Check filters; status bar shows <em>filtered</em> totals.</li>
                </ul>
            </body>
            </html>
            """,

            # Chart info
            "chart_y_total": "Total ($)",
            "chart_y_amount": "Amount ($)",
            "chart_no_budget": "No budget",
            "chart_no_data": "No data",
        },
    },

    "es": {
        # --- CSV + data model structure (used by GUI core) ---
        "csv_headers": ["Monto", "Categoría", "Subcategoría", "Descripción", "Fecha", "Nombre"],
        "categories": {
            "housing": "Vivienda",
            "food": "Alimentación",
            "transport": "Transporte",
            "personal": "Personal",
            "lifestyle": "Estilo de Vida",
            "work": "Trabajo",
            "finance": "Finanzas",
            "other": "Otro",
        },
        "subcategories": {
            "rent": "Alquiler",
            "mortgage": "Hipoteca",
            "utilities": "Servicios",
            "insurance": "Seguro",
            "groceries": "Supermercado",
            "restaurants": "Restaurantes",
            "delivery": "Entrega a domicilio",
            "fuel": "Combustible",
            "public_transport": "Transporte público",
            "private_transport": "Transporte privado",
            "car_maintenance": "Mantenimiento de auto",
            "parking": "Estacionamiento",
            "clothing": "Ropa",
            "healthcare": "Salud",
            "gym": "Gimnasio",
            "personal_care": "Cuidado personal",
            "jupiter": "Jupiter",
            "entertainment": "Entretenimiento",
            "travel": "Viaje",
            "gaming": "Videojuegos",
            "events": "Eventos",
            "education": "Educación",
            "certifications": "Certificaciones",
            "work_supplies": "Material de trabajo",
            "subscriptions": "Suscripciones",
            "loan_payment_principal": "Pago de Préstamo (Capital)",
            "loan_interest": "Interés de Préstamo",
            "investment_contribution": "Aporte a Inversión",
            "savings_contribution": "Aporte a Ahorros",
            "debt_payment": "Pago de Deuda",
            "brokerage_fees": "Comisiones de Correduría",
            "bank_fees": "Comisiones Bancarias",
            "gifts": "Regalos",
            "donations": "Donaciones",
            "misc": "Varios",
        },
        "category_groups": {
            "housing": ["rent", "mortgage", "utilities", "insurance"],
            "food": ["groceries", "restaurants", "delivery"],
            "transport": ["fuel", "public_transport", "private_transport", "car_maintenance", "parking"],
            "personal": ["clothing", "healthcare", "gym", "personal_care", "jupiter"],
            "lifestyle": ["entertainment", "travel", "gaming", "events"],
            "work": ["education", "certifications", "work_supplies", "subscriptions"],
            "finance": [
                "loan_payment_principal",
                "loan_interest",
                "investment_contribution",
                "savings_contribution",
                "debt_payment",
                "brokerage_fees",
                "bank_fees",
            ],
            "other": ["gifts", "donations", "misc"],
        },

        # --- GUI strings ---
        "gui": {
            # Tabs
            "tab_browse": "Explorar",
            "tab_reports": "Reportes",
            "tab_budget": "Presupuesto",
            "tab_help": "Ayuda",

            # Browse tab: Filters
            "browse_filters_group": "Filtros",
            "browse_filter_name": "Nombre:",
            "browse_filter_month": "Mes:",
            "browse_filter_category": "Categoría:",
            "browse_filter_subcategory": "Subcategoría:",
            "browse_filter_desc": "Desc.:",
            "browse_apply_filters": "Aplicar filtros",
            "browse_clear_filters": "Limpiar",

            # Browse tab: Table
            "browse_edit_selected": "Editar seleccionado",
            "browse_delete_selected": "Eliminar seleccionado",

            # Browse tab: Quick Add
            "browse_quick_group": "Agregar rápido",
            "browse_quick_amount": "Monto",
            "browse_quick_category": "Categoría",
            "browse_quick_subcategory": "Subcategoría",
            "browse_quick_date": "Fecha",
            "browse_quick_desc": "Desc.",
            "browse_quick_name": "Nombre",
            "browse_quick_add_button": "Agregar",

            # Reports tab: Filters & labels
            "reports_filters_group": "Filtros",
            "reports_filter_name": "Nombre:",
            "reports_filter_month": "Mes:",
            "reports_filter_category": "Categoría:",
            "reports_filter_subcategory": "Subcategoría:",
            "reports_apply": "Aplicar",
            "reports_clear": "Limpiar",
            "reports_top_categories_bar": "Categorías principales (Barra)",
            "reports_category_mix_pie": "Mezcla por categoría (Pastel)",
            "reports_totals_by_category": "Totales por categoría",
            "reports_totals_by_subcategory": "Totales por subcategoría (Top 20)",

            # Reports tab: Table headers
            "reports_header_category": "Categoría",
            "reports_header_subcategory": "Subcategoría",
            "reports_header_total": "Total",

            # Budget tab: Filters
            "budget_filters_group": "Filtros",
            "budget_filter_month": "Mes:",
            "budget_apply": "Aplicar",
            "budget_clear": "Limpiar",

            # Budget tab: Income group
            "budget_income_group": "Agregar ingreso",
            "budget_income_month": "Mes",
            "budget_income_month_placeholder": "AAAA-MM",
            "budget_income_employer": "Empleador",
            "budget_income_biweekly": "Quincenal",
            "budget_income_dists": "Pagos",
            "budget_income_other": "Otro",
            "budget_income_add_update": "Agregar/Actualizar",

            # Budget tab: Budget group
            "budget_budget_month": "Mes",
            "budget_budget_category": "Categoría",
            "budget_budget_amount": "Monto",
            "budget_budget_add_update": "Agregar/Actualizar",
            "budget_add_group": "Agregar presupuesto (Plantilla anual)",
            "msg_prompt_create_budget_template": "Todavía no existe una plantilla de presupuesto. ¿Crear una plantilla para {year} ahora?",
            "msg_budget_template_saved": "Plantilla de presupuesto guardada para {year}.",
            "msg_confirm_budget_template_update": (
                "Estás actualizando el monto mensual de la plantilla de presupuesto para {category} en {year}.\n\n"
                "Monto mensual anterior: ${old}\n"
                "Monto mensual nuevo: ${new}\n\n"
                "Este monto mensual se usará para cada mes de {year}."
            ),
            "help_budget_template_note": (
                "Los presupuestos se guardan como una plantilla por año: un monto mensual por categoría para el año seleccionado."
            ),

            # Budget tab: Summary / charts / tables labels
            "budget_income_summary_label": "Resumen de ingresos",
            "budget_bva_bar_label": "Presupuesto vs real (Barra)",
            "budget_bva_table_label": "Presupuesto vs real",
            "budget_breakdown_label": "Desglose de presupuesto",
            "budget_mix_pie_label": "Mezcla de presupuesto (Pastel)",

            # Budget tab: IncomeSummaryModel headers
            "budget_income_header_employer": "Empleador",
            "budget_income_header_biweekly": "Quincenal",
            "budget_income_header_dists": "Pagos",
            "budget_income_header_other": "Otro",
            "budget_income_header_month_total": "Total mensual",
            "budget_income_header_expense_total": "Total de gastos",
            "budget_income_header_variance": "Varianza",

            # Budget tab: BudgetVsActualModel headers
            "budget_bva_header_category": "Categoría",
            "budget_bva_header_budget": "Presupuesto",
            "budget_bva_header_actual": "Real",
            "budget_bva_header_variance": "Varianza",

            # Menus
            "menu_file": "Archivo",
            "menu_file_new_csv": "Nuevo CSV",
            "menu_file_open_csv": "Abrir CSV",
            "menu_file_exit": "Salir",
            "menu_actions": "Acciones",
            "menu_actions_totals": "Totales",
            "menu_help": "Ayuda",
            "menu_help_item": "Ayuda",
            "menu_language": "Idioma",
            "menu_language_english": "Inglés",
            "menu_language_spanish": "Español",
            "msg_language_changed_restart": "Idioma actualizado. Reinicia la aplicación para que todas las etiquetas se actualicen en todas partes.",

            # Dialog titles
            "dlg_new_csv_title": "Nuevo CSV de gastos",
            "dlg_open_csv_title": "Abrir CSV de gastos",
            "dlg_error_title": "Error",
            "dlg_info_title": "Información",
            "dlg_totals_title": "Totales",
            "dlg_confirm_delete_title": "Confirmar eliminación",
            "dlg_confirm_exit_title": "Confirmar salida",
            "msg_csv_loaded_empty": "Se abrió el archivo CSV, pero no se pudieron interpretar filas. El archivo puede estar mal formado o usar encabezados inesperados.",

            # Dialog / message bodies
            "msg_location_not_writable": "La ubicación seleccionada no permite escritura.",
            "msg_no_csv_open": "Primero abre o crea un archivo CSV.",
            "msg_invalid_amount": "El monto debe ser un número, por ejemplo 12.34 o (12.34).",
            "msg_invalid_date": "La fecha debe tener el formato AAAA-MM-DD.",
            "msg_invalid_cat_sub": "Elige una combinación válida de categoría/subcategoría.",
            "msg_expense_saved": "Gasto agregado.",
            "msg_edit_select_one": "Selecciona exactamente una fila para editar.",
            "msg_delete_select": "Selecciona una o más filas para eliminar.",
            "msg_confirm_delete_body": "¿Eliminar {count} fila(s) seleccionada(s)? Esto no se puede deshacer.",
            "msg_totals_none": "No hay gastos que coincidan con los filtros actuales.",
            "msg_close_confirm_body": "¿Seguro que quieres cerrar Expense Tracker?",
            "msg_month_adjusted": "Se interpretó '{raw}' como '{normalized}'. Usa AAAA-MM o un mes como '2'/'Feb'.",
            "budget_budget_year": "Año",
            "budget_income_items_label": "Ingresos guardados",
            "budget_income_edit_selected": "Editar seleccionado",
            "budget_income_delete_selected": "Eliminar seleccionado",
            "dlg_confirm_title": "Confirmar",
            "msg_income_select_one": "Selecciona exactamente una fila de ingreso para editar.",
            "msg_income_delete_select": "Selecciona una o más filas de ingreso para eliminar.",
            "msg_confirm_delete_income_body": "¿Eliminar {count} fila(s) de ingreso seleccionada(s)? Esto no se puede deshacer.",
            "msg_income_saved": "Ingreso guardado.",
            "msg_budget_year_invalid": "El año debe tener 4 dígitos (se recibió '{raw}').",
            "menu_manage_categories": "Administrar categorías…",
            "dlg_manage_categories_title": "Administrar categorías",
            "lbl_categories": "Categorías",
            "lbl_subcategories": "Subcategorías",
            "btn_add": "Agregar",
            "btn_edit": "Editar",
            "btn_archive": "Archivar",
            "btn_restore": "Restaurar",
            "btn_close": "Cerrar",
            "lbl_label_en": "Etiqueta (Inglés)",
            "lbl_label_es": "Etiqueta (Español)",
            "msg_select_category_first": "Seleccione una categoría primero.",
            "msg_select_item_first": "Seleccione un elemento primero.",
            "msg_name_required": "Por favor ingrese un nombre.",
            "msg_confirm_archive": "¿Archivar '{name}'? Los gastos existentes no cambiarán.",
            "msg_confirm_restore": "¿Restaurar '{name}'?",
            "dlg_input_title": "Entrada",
            "prompt_new_category": "Nombre de la nueva categoría (Inglés):",
            "prompt_new_subcategory": "Nombre de la nueva subcategoría (Inglés):",
            "prompt_edit_category": "Editar nombre de la categoría (Inglés):",
            "prompt_edit_subcategory": "Editar nombre de la subcategoría (Inglés):",
            "menu_tools": "Herramientas",
            "msg_cannot_archive_last_category": "No puede archivar la última categoría activa.",
            "msg_cannot_archive_last_subcategory": "No puede archivar la última subcategoría activa.",
            "prompt_new_category_es": "Etiqueta en español para la nueva categoría (opcional)",
            "prompt_new_subcategory_es": "Etiqueta en español para la nueva subcategoría (opcional)",

            # Generic labels used in tables/charts
            "label_total": "Total",
            "label_overall_total": "Total general",
            "label_no_data": "Sin datos",
            "label_no_budget": "Sin presupuesto",

            # Status bar
            "status_rows_total": "{rows} filas • ${total:.2f} total",

            # App title
            "app_title": "Expense Tracker",

            # File / CSV / save errors
            "msg_csv_not_writable": "No se puede escribir en el CSV.",
            "msg_save_failed": "Error al guardar: {error}",

            # Income / Budget validation
            "msg_income_biweekly_nan": "El monto quincenal debe ser un número.",
            "msg_income_other_nan": "El campo 'Otro' debe ser un número.",
            "msg_choose_category": "Elige una categoría.",
            "msg_amount_must_be_number": "El monto debe ser un número.",
            "msg_income_employer_required": "El empleador es obligatorio.",

            # Edit dialog + buttons
            "dlg_edit_title": "Editar gasto",
            "dlg_edit_amount": "Monto",
            "dlg_edit_description": "Descripción",
            "dlg_edit_date": "Fecha (AAAA-MM-DD)",
            "dlg_edit_name": "Nombre",
            "btn_ok": "OK",
            "btn_cancel": "Cancelar",

            # Income month tooltip
            "budget_income_month_tooltip": "Ingresa AAAA-MM (ejemplo: 2026-01)",

            # Help
            "help_title": "Expense Tracker — Ayuda y Guía",

            # Help HTML
            "help_html": """
            <html>
            <head>
                <style>
                    body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
                    h1, h2, h3 { margin: 0.6em 0 0.3em; }
                    h1 { font-size: 18px; }
                    h2 { font-size: 16px; }
                    h3 { font-size: 14px; }
                    p, li { line-height: 1.35; }
                    code, kbd { background:#f5f5f5; padding:2px 4px; border-radius:4px; }
                    .box { border:1px solid #ddd; border-radius:6px; padding:12px; background:#fafafa; }
                    .toc a { text-decoration:none; }
                    .def-table { border-collapse: collapse; width: 100%; }
                    .def-table th, .def-table td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
                    .def-table th { background:#f7f7f7; text-align:left; }
                    .tip { background:#eef9f1; border:1px solid #c9ecd6; padding:8px; border-radius:6px; }
                    .warn { background:#fff7e6; border:1px solid #ffe0a3; padding:8px; border-radius:6px; }
                </style>
            </head>
            <body>
                <div class="box toc">
                    <strong>Tabla de Contenidos</strong>
                    <ol>
                        <li><a href="#getting-started">Primeros Pasos</a></li>
                        <li><a href="#browse">Pestaña Explorar</a></li>
                        <li><a href="#reports">Pestaña Reportes</a></li>
                        <li><a href="#budget">Pestaña Presupuesto</a></li>
                        <li><a href="#definitions">Definiciones (Glosario)</a></li>
                        <li><a href="#shortcuts">Atajos de Teclado</a></li>
                        <li><a href="#troubleshooting">Solución de Problemas</a></li>
                    </ol>
                </div>

                <h1 id="getting-started">Primeros Pasos</h1>
                <p>
                    Use <strong>Archivo → Nuevo CSV</strong> para crear un nuevo archivo de gastos (con encabezados),
                    o <strong>Archivo → Abrir CSV</strong> para abrir uno existente. La barra de estado en la
                    parte inferior muestra las <em>filas visibles</em> y su <em>total</em> después de aplicar filtros.
                </p>
                <p class="tip"><strong>Consejo:</strong> Los montos pueden ingresarse como <code>12.34</code> o <code>(12.34)</code> para valores negativos.</p>

                <h2 id="manage-categories">Administrar Categorías y Subcategorías</h2>
                <p>Puede agregar, editar, archivar o restaurar categorías y subcategorías usadas en toda la aplicación.</p>
                <ol>
                    <li>Vaya a <b>Herramientas → Administrar categorías</b>.</li>
                    <li>Seleccione una categoría para ver sus subcategorías.</li>
                    <li>Use <b>Agregar</b>, <b>Editar</b>, <b>Archivar</b> o <b>Restaurar</b>.</li>
                </ol>
                <ul>
                    <li><b>Archivar</b> oculta el elemento de las listas, pero mantiene los gastos/presupuestos existentes.</li>
                    <li>Si un elemento está en uso, puede seguir apareciendo en reportes/tablas por datos históricos, pero no estará disponible para nuevas capturas.</li>
                </ul>

                <h1 id="browse">Pestaña Explorar</h1>
                <h3>Filtros</h3>
                <ul>
                    <li><strong>Nombre</strong> — coincidencia exacta en la columna Nombre.</li>
                    <li><strong>Mes</strong> — acepta <code>1</code>, <code>Jan</code>, <code>January</code> (inglés/español compatibles).</li>
                    <li><strong>Categoría/Subcategoría</strong> — seleccione de las listas (etiquetas traducidas compatibles).</li>
                    <li><strong>Desc</strong> — coincidencia parcial sin distinguir mayúsculas/minúsculas en la Descripción.</li>
                </ul>
                <p>
                    Haga clic en <strong>Aplicar Filtros</strong> para filtrar; <strong>Limpiar</strong> restablece todo.
                    Haga clic derecho en la tabla para <em>Editar</em> o <em>Eliminar</em>. Seleccione una fila y presione
                    <strong>Editar Seleccionado</strong> para cambiar Monto, Descripción, Fecha o Nombre.
                </p>

                <h3>Agregar Rápido</h3>
                <ul>
                    <li>Ingrese el <strong>Monto</strong>, seleccione un par válido de <strong>Categoría/Subcategoría</strong>, establezca la <strong>Fecha</strong>, y opcionalmente agregue <strong>Desc</strong> y <strong>Nombre</strong>.</li>
                    <li>Haga clic en <strong>Agregar</strong>. Los datos se guardan inmediatamente en el CSV abierto.</li>
                </ul>
                <p class="warn"><strong>Nota:</strong> La Categoría/Subcategoría debe ser un par válido o el registro será rechazado.</p>

                <h1 id="reports">Pestaña Reportes</h1>
                <p>
                    Los reportes tienen sus propios filtros (separados de Explorar). El gráfico de <strong>Barras</strong> muestra las categorías principales,
                    y el gráfico <strong>Circular</strong> muestra la composición por categoría (la leyenda muestra porcentajes).
                </p>
                <ul>
                    <li>Las tablas de <strong>Totales por Categoría/Subcategoría</strong> incluyen una fila final de <em>Total</em> en negrita.</li>
                </ul>

                <h1 id="budget">Pestaña Presupuesto</h1>
                <h3>Filtros</h3>
                <p>
                    Use los menús desplegables de <strong>Año</strong> y <strong>Mes</strong> para enfocar la vista de Presupuesto.
                    La selección afecta los gastos <strong>Reales</strong> y los cálculos de ingresos para ese año/mes específico.
                </p>
                <p class="tip">
                    <strong>Consejo:</strong> Las entradas de ingresos se asocian por <code>YYYY-MM</code> (por ejemplo, <code>2026-01</code>), por lo que el mismo mes en años distintos se trata por separado.
                </p>

                <h3>Agregar Ingreso</h3>
                <ul>
                    <li><strong>Mes</strong> (acepta <code>YYYY-MM</code>, <code>YYYY-MM-DD</code> o un mes como <code>3</code>/<code>Mar</code>), <strong>Empleador</strong>, monto <strong>Quincenal</strong>, número de <strong>Distribuciones</strong> (2 o 3), y cualquier <strong>Otro</strong> ingreso.</li>
                    <li>Haga clic en <strong>Agregar/Actualizar</strong> para insertar o actualizar por (<em>mes</em>, <em>empleador</em>).</li>
                </ul>

                <h3>Agregar Presupuesto (Plantilla Anual)</h3>
                    <ul>
                        <li>Ingrese un <strong>Año</strong>, elija una <strong>Categoría</strong> e ingrese un <strong>Monto</strong>, luego haga clic en <strong>Agregar/Actualizar</strong>.</li>
                        <li>Este monto se trata como una <strong>plantilla de presupuesto mensual</strong> para esa categoría en el año seleccionado.</li>
                        <li>La vista Presupuesto vs Real compara los gastos <strong>Reales</strong> del mes seleccionado contra los montos de la <strong>plantilla mensual</strong> guardada para ese año.</li>
                    </ul>

                <h3>Resumen de Ingresos (franja superior)</h3>
                <ul>
                    <li><strong>Total del Mes</strong> — calculado como <em>Quincenal × Distribuciones + Otros</em>.</li>
                    <li><strong>Total de Gastos</strong> — suma de todos los gastos reales del mes seleccionado.</li>
                    <li><strong>Variación</strong> — <em>Total del Mes − Total de Gastos</em> (verde si ≥ 0, rojo si &lt; 0).</li>
                </ul>

                <h3>Presupuesto vs Real</h3>
                <ul>
                    <li>La tabla izquierda muestra <em>Presupuesto</em>, <em>Real</em> y <em>Variación</em> por categoría (Real ≤ Presupuesto en verde, de lo contrario rojo).</li>
                    <li>El gráfico de barras compara Presupuesto vs Real; la leyenda se muestra sobre el área del gráfico.</li>
                    <li>La tabla derecha enumera el <em>Desglose del Presupuesto</em> con una fila final de <em>Total</em>.</li>
                    <li>El gráfico circular muestra la <em>Composición del Presupuesto</em>.</li>
                </ul>

                <h1 id="definitions">Definiciones (Glosario)</h1>
                <table class="def-table">
                    <tr><th>Término</th><th>Significado</th></tr>
                    <tr><td><strong>Monto</strong></td><td>El valor de la transacción. Los negativos pueden ingresarse como <code>(12.34)</code>.</td></tr>
                    <tr><td><strong>Categoría / Subcategoría</strong></td><td>Claves de clasificación usadas para reportes y presupuestos.</td></tr>
                    <tr><td><strong>Mes</strong></td><td>El filtro acepta meses numéricos o por nombre (<em>Jan</em>/<em>Enero</em>, etc.).</td></tr>
                    <tr><td><strong>Presupuesto</strong></td><td>El gasto <strong>mensual</strong> planificado por categoría almacenado como plantilla para el <strong>año</strong> seleccionado.</td></tr>             
                    <tr><td><strong>Real</strong></td><td>La suma de los gastos reales registrados para esa categoría/mes.</td></tr>
                    <tr>
                        <td><strong>Variación</strong></td>
                        <td>
                            <ul style="margin:0; padding-left:18px;">
                                <li><strong>Presupuesto vs Real:</strong> <em>Real − Presupuesto</em> (verde cuando Real ≤ Presupuesto; rojo cuando Real &gt; Presupuesto).</li>
                                <li><strong>Resumen de Ingresos:</strong> <em>Total del Mes − Total de Gastos</em> (verde cuando ≥ 0; rojo cuando &lt; 0).</li>
                            </ul>
                        </td>
                    </tr>
                    <tr><td><strong>Distribuciones</strong></td><td>La cantidad de períodos de pago quincenales en el mes (2 o 3).</td></tr>
                    <tr><td><strong>Otros (Ingresos)</strong></td><td>Cualquier ingreso mensual que no esté incluido en el pago quincenal (por ejemplo, bonos, ingresos adicionales).</td></tr>
                </table>

                <h1 id="shortcuts">Atajos de Teclado</h1>
                <ul>
                    <li><strong>Ctrl+N</strong> — Nuevo CSV</li>
                    <li><strong>Ctrl+O</strong> — Abrir CSV</li>
                    <li><strong>Ctrl+T</strong> — Ventana de totales (Explorar)</li>
                    <li><strong>F1</strong> — Abrir pestaña de Ayuda</li>
                </ul>

                <h1 id="troubleshooting">Solución de Problemas</h1>
                <ul>
                    <li><strong>No puedo guardar:</strong> Asegúrese de que la ubicación del CSV tenga permisos de escritura.</li>
                    <li><strong>Las categorías no coinciden:</strong> Seleccione un par válido de Categoría/Subcategoría de las listas.</li>
                    <li><strong>Fechas rechazadas:</strong> Use <code>YYYY-MM-DD</code>.</li>
                    <li><strong>Los totales parecen incorrectos:</strong> Revise los filtros; la barra de estado muestra los totales <em>filtrados</em>.</li>
                </ul>
            </body>
            </html>
            """,

            # Chart info
            "chart_y_total": "Total ($)",
            "chart_y_amount": "Monto ($)",
            "chart_no_budget": "Sin presupuesto",
            "chart_no_data": "Sin datos",
        },
    },
}
