# Technical Documentation

This document describes the current technical design after the project was refactored into per-tab workflow packages.

---

## 1. Technology stack

| Area | Technology |
|---|---|
| Desktop GUI | `customtkinter`, `tkinter`, `ttk` |
| Excel reading/writing | `pandas`, `openpyxl` |
| Charts/formatting | `openpyxl.chart`, `openpyxl.styles` |
| Logging | Python `logging` plus GUI log handler |
| Memory tracking | `tracemalloc`, `gc` |
| Tests | `pytest`, `unittest`, source-level contract checks |

---

## 2. Entry point and shared state

The application starts in `main.py`.

`App` is the root `customtkinter.CTk` controller. It:

1. Sets theme defaults.
2. Creates a shared `state_data` dictionary.
3. Instantiates `LiveMetrics` from `state/app_state.py`.
4. Creates the shared logger.
5. Routes the user through Window 1, Window 2, Window 3, and Window 4.

Shared state keys:

- `entry_mode`
- `selected_project`
- `selected_scanner`
- `theme_name`
- `last_output_file`
- `live_metrics`
- `ui_hooks` once the dashboard is built

---

## 3. GUI architecture

```text
main.py
  └─ gui/window1_entry.py
      └─ gui/window2_project_selection.py
          └─ gui/window3_scanner_selection.py
              └─ gui/window4_main.py
```

### Wizard windows

- `Window1Entry`: selects VNF/CNF entry mode.
- `Window2ProjectSelection`: selects the project profile.
- `Window3ScannerSelection`: selects the scanner profile.

### Main dashboard

`gui/window4_main.py` hosts the operational UI. It builds:

- `HeaderPanel`
- `Sidebar`
- `SummaryCards`
- `WorkflowStepper`
- `CTkTabview`
- `LogsPanel`
- status bar

The dashboard uses a vertical `tk.PanedWindow` so the logs area can be resized by dragging the splitter.

### Dashboard tabs

```python
["📄 Make Report", "📊 Generate Tracking", "🛡 Add VAMS Data", "📈 Show Summary"]
```

The first three tabs are processing workflows. The fourth tab opens the latest output workbook on the Dashboard/Summary sheet.

---

## 4. Live metric architecture

`state/app_state.py` defines `LiveMetrics`.

Fields:

- `total_vulns`
- `unique_vulns`
- `processing_time`
- `success_rate`
- `_started_at`
- `_subs`

Lifecycle:

1. `start()` resets time/rate and stores start time.
2. `tick()` updates elapsed seconds while the process is running.
3. `stop(success=True)` finalizes elapsed time and sets success rate to `100`.
4. `reset()` clears metrics.
5. `notify()` pushes updates into subscribed UI callbacks.

`Window4Main` subscribes the header cards to `LiveMetrics`. The card values and their smaller tag labels update together.

Metric sources:

- Vulnerabilities Processed: non-empty `Name`/alias entries in Total-like sheets.
- Unique Vulnerabilities: non-empty `Name`/alias entries in Unique-like sheets.
- Processing Time: elapsed seconds from `LiveMetrics`.
- Success Rate: stage progress converted to percent, then `100%` on success.

---

## 5. Tab-owned architecture

The root `logic/` package is intentionally removed. Every workflow owns its own processing modules.

### Why this design exists

The user requirement was that changes to logic for one tab should not affect the other tabs. For that reason, parser, comparison/enrichment, Excel writer, reader, formatting, and 3UK Qualys logic are copied into each tab package as local ownership boundaries.

### Package pattern

```text
tabs/<workflow>/
  <workflow_ui>.py
  parser.py
  logic.py
  comparison_logic.py or enrichment modules
  excel_writer/
    __init__.py
    formatting.py
    reader.py
    sheets.py
    three_uk_qualys.py
    workbook.py
```

The small `logic.py` files are import boundaries. The heavier implementation lives in parser, comparison/enrichment, and Excel writer modules.

---

## 6. Make Report technical flow

Main UI file: `tabs/make_new_report/make_new_report.py`

Local processing files:

- `tabs/make_new_report/parser.py`
- `tabs/make_new_report/comparison_logic.py`
- `tabs/make_new_report/logic.py`
- `tabs/make_new_report/excel_writer/*`

Flow:

```text
Validate raw file + raw sheet + output path
  ↓
If 3UK + Qualys: build special total/unique DataFrames
Else: parse raw scanner sheet through local parser
  ↓
Aggregate unique findings
  ↓
write_output()
  ↓
apply_table_formatting()
  ↓
Update last output path, dashboard metrics, logs, run status
```

Primary output sheets:

- `Dashboard`
- `Total Vulnerabilities`
- `Unique Vulnerabilities`
- `Disposition`

---

## 7. Generate Tracking technical flow

Main UI file: `tabs/generate_tracking/generate_tracking.py`

Local processing files:

- `tabs/generate_tracking/parser.py`
- `tabs/generate_tracking/comparison_logic.py`
- `tabs/generate_tracking/logic.py`
- `tabs/generate_tracking/excel_writer/*`

Flow:

```text
Validate master file/sheet + raw file/sheet + output path
  ↓
Parse raw scanner sheet
  ↓
Parse required master sheet
  ↓
classify_new_old(raw_df, master_df)
  ↓
new_df + old_df
  ↓
Map 3UK + Qualys Total/New/Old/Unique outputs into template columns when needed
  ↓
aggregate_unique(raw_df) / build 3UK + Qualys unique template output
  ↓
write_output(output, new_df, old_df, unique_df, total_df=total_df)
```

Important implementation rule:

- `total_df` contains all parsed raw findings and is written to `Total Vulnerabilities`.
- `new_df` contains raw findings not matched in the master tracking sheet and is written to `New Vulnerabilities`.
- `old_df` contains raw findings matched in the master tracking sheet and is written to `Old Vulnerabilities`.
- `unique_df` contains aggregated total findings and is written to `Unique Vulnerabilities`.

---

## 8. Add VAMS Data technical flow

Main UI file: `tabs/add_vams_data/add_vams_data.py`

Local processing files:

- `tabs/add_vams_data/parser.py`
- `tabs/add_vams_data/logic.py`
- `tabs/add_vams_data/fast_vams_enrichment.py`
- `tabs/add_vams_data/vams_enrichment.py`
- `tabs/add_vams_data/excel_writer/*`

Flow:

```text
Validate existing output workbook + VAMS source file/sheet
  ↓
Read generated Total/Unique sheets
  ↓
Parse VAMS source without severity filtering
  ↓
Build fast VAMS lookup engine
  ↓
Enrich Unique and Total data
  ↓
Write VAMS-managed columns only
  ↓
Refresh Dashboard charts
  ↓
Save workbook
```

The writeback is non-destructive: only VAMS-managed columns are updated, and existing manually filled values are preserved where the target cell is not empty.

---

## 9. Parser behavior

Each tab has its own `parser.py`. The parser responsibilities are:

- Detect the header row from the first rows of an Excel sheet.
- Normalize scanner-specific column names into the standard template.
- Map aliases such as `Severity` to `Risk`, `IP`/`Host` to `Host / Image`, and `QID`/`Plugin ID` to `Scanner ID`.
- Split embedded host/port values where possible.
- Normalize severities.
- Filter supported severities when requested.
- Build comparison/matching keys.

Standard severity order:

```text
Critical > High > Medium > Low
```

---

## 10. Comparison and aggregation behavior

Each comparison module includes:

- `classify_new_old(raw_df, master_df)`
- `aggregate_unique(df)`

`classify_new_old` builds row keys and splits raw rows based on whether their key exists in master data.

`aggregate_unique` groups duplicate findings and merges repeated values with comma-separated de-duplication while retaining the highest severity.

---

## 11. VAMS enrichment behavior

Add VAMS Data uses `FastVamsEnrichmentEngine` from `tabs/add_vams_data/fast_vams_enrichment.py`.

The engine:

1. Builds multiple tiered keys per VAMS row.
2. Stores lookup dictionaries by matching tier.
3. Builds matching keys for target rows.
4. Copies VAMS-managed values into matching output rows.

Important matching fields:

- `Name`
- `Host / Image`, `Host`, `IP`
- `Port`
- `CVE`
- `Scanner ID`, `Plugin ID`, `QID`

---

## 12. Excel writer behavior

Each tab owns an `excel_writer/` package.

### `workbook.py`

Workbook-level orchestration:

- Create/open workbook.
- Normalize sheet names.
- Create dashboard sheet.
- Write data sheets.
- Write Disposition sheet.
- Auto-fit columns.
- Save workbook.

### `sheets.py`

Sheet-level writing:

- Write headers and rows.
- Clear/rebuild dashboard.
- Create pie and bar charts.
- Hide chart-source columns.
- Write Disposition template.

Dashboard clearing is defensive against stale merged-cell metadata from Excel/openpyxl. If an unmerge operation raises expected stale-range errors, the range is discarded and dashboard refresh continues.

### `formatting.py`

Styling helpers:

- Header styling.
- Metadata row styling.
- Table formatting.
- Borders/alignment.
- Column auto-width.

### `reader.py`

Reads generated workbook sheets into DataFrames and maps display column aliases back into standard column names.

### `three_uk_qualys.py`

Special 3UK + Qualys support:

- Detect Qualys header rows.
- Map Qualys fields.
- Build 3UK-specific total and unique views.
- Support VAMS matching for the special layout.

---

## 13. Visual modules

`visuals/highlight_logic.py` maps severity values to Excel fills.

`visuals/summary/summary_generator.py` builds DataFrames for:

- severity counts,
- severity chart data,
- reported vs expert severity,
- disposition counts.

`visuals/summary/summary_generator.py` exposes the Add VAMS Data tab-local dashboard writer for summary refreshes.

---

## 14. Utilities

- `utils/file_handler.py`: Excel file validation and sheet listing.
- `utils/logger.py`: shared logger and GUI log streaming handler.
- `utils/memory.py`: memory tracking context manager and cleanup helper.

---

## 15. Tests and contracts

`testcases/` is not runtime code, but it is important development protection.

Current test coverage verifies:

- Required files exist.
- The root `logic/` package remains removed.
- Each tab owns parser/logic/excel writer modules.
- Important Excel writer exports are available.
- Dashboard charts/layout contracts remain valid.
- UI contracts such as Show Summary, reset, logs behavior, and metric cards remain in place.

Run:

```bash
python -m pytest -q
python -m compileall -q .
```
