# Full Project Documentation

This is the complete up-to-date documentation for the current project structure and behavior.

---

## 1. Project overview

**Vulnerability Management Excel Automation** is a desktop GUI application for processing vulnerability-management Excel data. It is designed for users who need repeatable, formatted outputs from scanner exports, master/history files, and VAMS remediation data.

The project now uses a **tab-owned architecture**. Each operational workflow has its own parser, logic, and Excel writer modules in its own tab folder. This is intentional: if one tab's logic changes, the other tab workflows remain isolated.

---

## 2. What the application produces

Depending on the workflow, generated or updated workbooks can include:

- `Dashboard`
- `Total Vulnerabilities`
- `Old Vulnerabilities`
- `Unique Vulnerabilities`
- `Disposition`

The Excel Dashboard contains severity and VAMS/disposition summaries. Dashboard source data is written to hidden columns so the visible sheet remains clean.

---

## 3. Application startup

Entry point: `main.py`

Startup sequence:

1. Create the root `App` window.
2. Configure CustomTkinter appearance.
3. Initialize shared `state_data`.
4. Store a `LiveMetrics` object.
5. Create the shared logger.
6. Display `Window1Entry`.
7. Route through project/scanner wizard windows.
8. Display `Window4Main` dashboard.

Shared state is passed into every window and tab, allowing tabs to update the dashboard without direct circular dependencies.

---

## 4. GUI windows

### `gui/window1_entry.py`

First wizard screen. Lets the user choose the entry mode:

- `VNF`
- `CNF`

The selected mode is saved into shared state.

### `gui/window2_project_selection.py`

Second wizard screen. Lets the user choose the project/customer profile. The choice is saved in `selected_project`.

### `gui/window3_scanner_selection.py`

Third wizard screen. Lets the user choose the scanner profile, such as Nessus, Qualys, or Anchor. The choice is saved in `selected_scanner`.

### `gui/window4_main.py`

Main dashboard screen. It contains the operational tabs, logs, metrics, navigation, and UI hooks.

Important responsibilities:

- Build the dashboard layout.
- Create the tab view.
- Load the three processing tabs.
- Build the `Show Summary` tab.
- Manage live run state.
- Update stage progress.
- Count output-sheet rows for metric cards.
- Reset the current workflow tab.
- Export logs.
- Open output files.
- Open summary dashboards.
- Support theme switching.

---

## 5. GUI component modules

### `gui/ui/cards.py`

Builds the four top dashboard KPI cards:

1. Vulnerabilities Processed
2. Unique Vulnerabilities
3. Processing Time
4. Success Rate

Each card has:

- a title,
- a large value,
- a small dynamic tag.

The tag shows count/status text such as:

- `Total sheet count: 2171`
- `Unique sheet count: 330`
- `Elapsed time: 65s`
- `Completion: 100%`

### `gui/ui/header.py`

Builds the header panel with app title, subtitle, theme, and run status.

### `gui/ui/logs_panel.py`

Builds the Live Logs panel. It contains a search entry, an Open Output File button, and a text box that receives log messages through `UILogHandler`.

### `gui/ui/sidebar.py`

Builds sidebar navigation:

- Dashboard
- Make Report
- Generate Tracking
- Add VAMS Data
- Show Summary

### `gui/ui/themes.py`

Defines color palettes for:

- Dark
- Light
- Cybersecurity Neon

Each palette includes a `muted` color to support secondary helper text.

### `gui/ui/workflow_stepper.py`

Displays workflow progress:

```text
Inputs → Parse → Compare → Enrich → Write
```

---

## 6. Runtime state

### `state/app_state.py`

Defines `LiveMetrics`, the shared runtime metrics dataclass.

Fields:

- `total_vulns`
- `unique_vulns`
- `processing_time`
- `success_rate`

Methods:

- `subscribe(fn)`
- `notify()`
- `reset()`
- `start()`
- `tick()`
- `stop(success=True)`

The dashboard subscribes to this object and updates metric cards whenever it changes.

### `state/__init__.py`

Package marker for runtime state modules.

---

## 7. Make Report workflow

Folder: `tabs/make_new_report/`

Purpose: create a new vulnerability report from a raw scanner file.

### Files

| File | Purpose |
|---|---|
| `make_new_report.py` | UI and run orchestration for the tab. |
| `parser.py` | Tab-local raw scanner parser. |
| `comparison_logic.py` | Tab-local unique aggregation logic. |
| `logic.py` | Small tab-local import boundary for report logic. |
| `excel_writer/__init__.py` | Public exports for the local Excel writer package. |
| `excel_writer/workbook.py` | Workbook-level output orchestration. |
| `excel_writer/sheets.py` | Sheet writing, Dashboard charts, Disposition sheet. |
| `excel_writer/formatting.py` | Table, header, metadata, border, and width formatting. |
| `excel_writer/reader.py` | Reads generated sheets into DataFrames when needed. |
| `excel_writer/three_uk_qualys.py` | Special 3UK + Qualys layout/parser helpers. |

### Run sequence

```text
User selects raw file/sheet/output path
  ↓
Validate inputs
  ↓
Parse raw data or use 3UK + Qualys builder
  ↓
Aggregate unique vulnerabilities
  ↓
Write output workbook
  ↓
Apply formatting
  ↓
Update state/logs/metrics
```

---

## 8. Generate Tracking workflow

Folder: `tabs/generate_tracking/`

Purpose: compare raw scanner findings with a required master workbook and generate tracking output.

### Files

| File | Purpose |
|---|---|
| `generate_tracking.py` | UI and run orchestration for tracking generation. |
| `parser.py` | Tab-local raw/master scanner parser. |
| `comparison_logic.py` | New-vs-old classification and unique aggregation. |
| `logic.py` | Small tab-local import boundary for tracking logic. |
| `excel_writer/__init__.py` | Public exports for the local Excel writer package. |
| `excel_writer/workbook.py` | Writes Dashboard, Total/New, Old, Unique, and Disposition sheets. |
| `excel_writer/sheets.py` | Sheet writing and chart dashboard logic. |
| `excel_writer/formatting.py` | Excel styling helpers. |
| `excel_writer/reader.py` | Reads generated sheets into DataFrames when needed. |
| `excel_writer/three_uk_qualys.py` | Special 3UK + Qualys support. |

### Run sequence

```text
User selects raw file/sheet/output path and required master file/sheet
  ↓
Validate inputs
  ↓
Parse raw file
  ↓
Parse master file if provided
  ↓
classify_new_old(raw_df, master_df)
  ↓
new_df + old_df
  ↓
aggregate_unique(raw_df)
  ↓
write_output(output, new_df, old_df, unique_df)
```

### Output mapping

| DataFrame | Output sheet |
|---|---|
| `total_df` / parsed raw data | `Total Vulnerabilities` |
| `new_df` / raw rows not matched in master tracking | `New Vulnerabilities` |
| `old_df` / raw rows matched in master tracking | `Old Vulnerabilities` |
| `unique_df` / aggregated total findings | `Unique Vulnerabilities` |

Generate Tracking writes Total/New/Old/Unique sheets in the template vulnerability columns.

---

## 9. Add VAMS Data workflow

Folder: `tabs/add_vams_data/`

Purpose: update an existing generated workbook with VAMS remediation information.

### Files

| File | Purpose |
|---|---|
| `add_vams_data.py` | UI and run orchestration for VAMS enrichment. |
| `parser.py` | Tab-local VAMS/source parser. |
| `logic.py` | Sheet-candidate constants and VAMS column exports. |
| `fast_vams_enrichment.py` | Fast tiered matching engine. |
| `vams_enrichment.py` | VAMS enrichment helpers and update logic. |
| `excel_writer/__init__.py` | Public exports for the local Excel writer package. |
| `excel_writer/workbook.py` | Workbook writer API kept local for this workflow. |
| `excel_writer/sheets.py` | Dashboard refresh and sheet helper logic. |
| `excel_writer/formatting.py` | Excel styling helpers. |
| `excel_writer/reader.py` | Reads generated output sheets for enrichment. |
| `excel_writer/three_uk_qualys.py` | Special 3UK + Qualys support. |

### Run sequence

```text
User selects existing output workbook and VAMS source
  ↓
Validate inputs
  ↓
Read generated Total/Unique sheets
  ↓
Parse VAMS source
  ↓
Build FastVamsEnrichmentEngine lookup tables
  ↓
Enrich matching rows
  ↓
Write only VAMS-managed columns back
  ↓
Refresh Dashboard
  ↓
Save workbook
```

### VAMS-managed columns

- `Release Remediation Plan`
- `Release Remediation Date`
- `Expert Severity`
- `Expert Score`
- `Remediation Reference ID`
- `Disposition`
- `VAMS (PSL comments)`
- `MSS Comments`

---

## 10. Parser details

Each tab has its own parser file. The parser normalizes source Excel data into a consistent vulnerability template.

Parser responsibilities:

- Header-row detection.
- Column alias mapping.
- Template column creation.
- Host/port cleanup.
- Severity normalization.
- Optional severity filtering.
- Matching-key generation.

Supported concepts include scanner aliases such as:

- `Plugin ID`, `QID`, `Scanner ID`
- `Severity`, `Risk`, numeric severity values
- `Host`, `IP`, `Hostname`, `Host / Image`
- `Title`, `Name`, plugin names

---

## 11. Excel writer details

Each workflow has its own local Excel writer package.

### Dashboard generation

Dashboard sheet writing includes:

- clearing prior dashboard content,
- safely removing stale merged ranges,
- writing chart source tables,
- hiding chart-source columns,
- adding severity pie charts,
- adding VAMS/disposition bar charts.

### Formatting

Formatting helpers apply:

- header styles,
- metadata rows,
- freeze panes,
- borders,
- alignment,
- risk highlighting,
- column auto-width.

### 3UK + Qualys

Each workflow's local `three_uk_qualys.py` contains the special profile behavior. This prevents edits to one tab's special handling from changing another tab.

---

## 12. Summary/chart generation

Folder: `visuals/summary/`

### `summary_generator.py`

Creates data summaries for dashboard charts:

- severity summary,
- severity chart summary,
- expert severity summary,
- disposition summary.

### `summary_generator.py`

Provides a small compatibility entry point to refresh summary/dashboard sheets through the Add VAMS Data tab-local writer.

---

## 13. Utility modules

### `utils/file_handler.py`

- Validates supported Excel file paths.
- Lists Excel sheet names.

### `utils/logger.py`

- Creates the shared logger.
- Defines `UILogHandler`, which streams logs into the GUI logs text box.

### `utils/memory.py`

- Tracks memory usage around heavy workflow runs.
- Releases large objects and triggers garbage collection.

---

## 14. Developer script

### `scripts/validate_vams_enrichment.py`

Command-line helper for debugging VAMS matching. It loads generated workbook data and a VAMS source, builds fast matching keys, and prints matching diagnostics.

This script is useful for development/support, but it is not required for normal GUI runtime.

---

## 15. Tests

Folder: `testcases/`

Test files:

- `test_summary/test_architecture_contracts.py`
- `test_summary/test_dashboard_layout.py`
- `test_summary/test_ui_contracts.py`
- `validation_engine.py`

The tests ensure:

- The architecture remains tab-owned.
- The root `logic/` package is not reintroduced.
- Important local writer exports remain available.
- UI features such as Show Summary, reset, logs, cards, and resizable panels remain present.
- Excel Dashboard chart contracts remain stable.

Run tests:

```bash
python -m pytest -q
```

Run syntax/bytecode check:

```bash
python -m compileall -q .
```

---

## 16. What can be excluded from a packaged customer app

For a runtime-only packaged application, these are normally optional:

- `docs/`
- `testcases/`
- `scripts/`

These are required for runtime:

- `main.py`
- `gui/`
- `state/`
- `tabs/`
- `utils/`
- `visuals/`
- runtime dependencies

---

## 17. Maintenance rules

1. Do not recreate the shared root `logic/` package.
2. Put workflow-specific changes inside that workflow's tab folder.
3. Keep parser changes tab-local unless all three tabs intentionally need the same change.
4. Keep Excel writer changes tab-local unless all three workflows intentionally need the same change.
5. Keep VAMS matching changes in `tabs/add_vams_data/` unless another tab explicitly needs matching behavior.
6. Run tests and compile checks after changes.
7. Update documentation when architecture, workflows, metrics, output sheets, or dependencies change.
