# 🛡️ Vulnerability Management Excel Automation

GUI-based desktop automation for vulnerability reporting, tracking, VAMS enrichment, and dashboard-ready Excel workbooks.

---

## Current purpose

This project helps vulnerability-management teams process scanner exports into standardized Excel outputs. It preserves the original business purpose while using a tab-isolated architecture so changes in one workflow do not accidentally break another workflow.

The application can:

- Parse scanner/VAMS Excel files into standard vulnerability columns.
- Build new vulnerability reports from raw scanner data.
- Generate tracking workbooks by comparing raw findings against a required master workbook.
- Add VAMS remediation fields into an existing generated workbook.
- Create/refresh Excel Dashboard charts and supporting sheets.
- Show live GUI metrics, logs, processing progress, and output summary access.

---

## Runtime requirements

- Python 3.10+
- GUI-capable OS/session with `tkinter`
- Python packages listed in `Requirements.txt`

Install the runtime packages:

```bash
python -m pip install -r Requirements.txt
```

Start the app:

```bash
python main.py
```

---

## User workflow

```text
Launch main.py
  ↓
Window 1: choose Entry Mode (VNF/CNF)
  ↓
Window 2: choose Project
  ↓
Window 3: choose Scanner
  ↓
Main Dashboard
  ├─ Make Report
  ├─ Generate Tracking
  ├─ Add VAMS Data
  └─ Show Summary
```

---

## Main dashboard features

The dashboard in `gui/window4_main.py` contains:

- Header with theme and run status.
- Sidebar navigation.
- Four live metric cards.
- Workflow stage stepper.
- Processing tabs.
- Dedicated **Show Summary** tab.
- Resizable Live Logs panel using a vertical `tk.PanedWindow`.
- Reset, theme switch, log export, and output-file opening controls.

### Live metric cards

The four header cards are implemented in `gui/ui/cards.py` and updated through `LiveMetrics` in `state/app_state.py`.

| Card | Meaning |
|---|---|
| Vulnerabilities Processed | Counts non-empty `Name`/alias entries from the output workbook Total sheet. |
| Unique Vulnerabilities | Counts non-empty `Name`/alias entries from the output workbook Unique sheet. |
| Processing Time | Live elapsed seconds while a workflow is running. |
| Success Rate | Stage-based completion percent; becomes `100%` on successful completion. |

The small tag under each card also displays the same live count/status, for example `Total sheet count: 2171` or `Completion: 100%`.

---

## Workflow tabs

### 1. Make Report

Package: `tabs/make_new_report/`

Purpose: create a fresh output workbook from a raw scanner export.

Inputs:

- Raw scanner Excel file.
- Raw sheet name.
- Output `.xlsx` path.

Processing:

1. Validate file/sheet/output path.
2. Parse and normalize raw data through the tab-local parser.
3. Build total and unique vulnerability data.
4. Use the tab-local Excel writer to write Dashboard, Total, Unique, and Disposition sheets.
5. Apply formatting and update GUI metrics/logs.

Special handling: 3UK + Qualys uses tab-local special builders in `tabs/make_new_report/excel_writer/three_uk_qualys.py`.

### 2. Generate Tracking

Package: `tabs/generate_tracking/`

Purpose: compare current raw scanner data against a required master workbook and produce tracking output.

Inputs:

- Required master Excel file and sheet.
- Raw scanner Excel file and sheet.
- Output `.xlsx` path.

Processing:

1. Validate selected files/sheets.
2. Parse raw data.
3. Parse required master data.
4. Classify rows into new and old findings with the tab-local comparison logic.
5. Aggregate unique findings.
6. Write the output workbook.

Important output rule:

- `total_df` / all parsed raw findings are written to **Total Vulnerabilities**.
- `new_df` / raw findings not matched in the master tracking sheet are written to **New Vulnerabilities**.
- `old_df` / raw findings matched in the master tracking sheet are written to **Old Vulnerabilities**.
- `unique_df` / aggregated total findings are written to **Unique Vulnerabilities**.

### 3. Add VAMS Data

Package: `tabs/add_vams_data/`

Purpose: enrich an existing generated workbook with VAMS-managed remediation fields.

Inputs:

- Existing generated output workbook.
- VAMS source Excel file and sheet.

Processing:

1. Read generated Total/Unique sheets.
2. Parse the incoming VAMS source with the tab-local parser.
3. Build fast tiered VAMS lookup keys.
4. Enrich matching rows.
5. Write only VAMS-managed columns back into the workbook.
6. Refresh Dashboard charts.
7. Save the workbook and update metrics/logs.

VAMS-managed columns:

- `Release Remediation Plan`
- `Release Remediation Date`
- `Expert Severity`
- `Expert Score`
- `Remediation Reference ID`
- `Disposition`
- `VAMS (PSL comments)`
- `MSS Comments`

### 4. Show Summary

Package/file: `gui/window4_main.py`

Purpose: open the latest selected/generated output file directly on the Dashboard or Summary sheet.

If the workbook can be edited, the app activates `Dashboard` or `Summary Data` before opening it. If the file is already open/locked by Excel, the app logs a warning and still opens the file.

---

## Tab-isolated architecture

The former shared root `logic/` package has been removed. Each workflow owns its own parser, comparison/enrichment logic, and Excel writer package.

```text
tabs/
  make_new_report/
    make_new_report.py
    parser.py
    logic.py
    comparison_logic.py
    excel_writer/
      __init__.py
      formatting.py
      reader.py
      sheets.py
      three_uk_qualys.py
      workbook.py

  generate_tracking/
    generate_tracking.py
    parser.py
    logic.py
    comparison_logic.py
    excel_writer/
      __init__.py
      formatting.py
      reader.py
      sheets.py
      three_uk_qualys.py
      workbook.py

  add_vams_data/
    add_vams_data.py
    parser.py
    logic.py
    fast_vams_enrichment.py
    vams_enrichment.py
    excel_writer/
      __init__.py
      formatting.py
      reader.py
      sheets.py
      three_uk_qualys.py
      workbook.py
```

This means:

- Make Report changes should stay inside `tabs/make_new_report/`.
- Generate Tracking changes should stay inside `tabs/generate_tracking/`.
- Add VAMS Data changes should stay inside `tabs/add_vams_data/`.
- Shared GUI/state/utilities stay in `gui/`, `state/`, `utils/`, and `visuals/`.

---

## Column expectations

### Standard vulnerability template

The parsers normalize scanner data into these common fields where possible:

- `Scanner ID`
- `CVE`
- `CVSS v2.0 Base Score`
- `Risk`
- `Host / Image`
- `Protocol`
- `Port`
- `Name`
- `Synopsis`
- `Description`
- `Solution`
- `See Also`
- `Plugin Output`
- `CVSS v3.0 Base Score`
- `CVSS v3.0 Temporal Score`
- VAMS-managed columns listed above

### Minimum raw data fields

For reliable parsing/comparison, raw inputs should contain recognizable equivalents of:

- `Name`
- `Host / Image`
- `Port`
- `CVE`
- `Risk`

Aliases such as `Title`, `IP`, `Host`, `Severity`, `Plugin ID`, `QID`, and scanner-specific headings are supported by the tab-local parsers.

### VAMS matching fields

VAMS matching works best when these fields are clean:

- `Name`
- `Host / Image` / `Host` / `IP`
- `Port`
- `CVE`
- `Scanner ID` / `Plugin ID` / `QID`

---

## Output workbook structure

Typical generated workbooks include:

- `Dashboard`
- `Total Vulnerabilities`
- `New Vulnerabilities`
- `Old Vulnerabilities`
- `Unique Vulnerabilities`
- `Disposition`

Generate Tracking writes Total/New/Old/Unique sheets in the template vulnerability columns.

---

## Important folders

| Folder | Purpose | Runtime required? |
|---|---|---|
| `gui/` | Wizard windows, dashboard shell, reusable UI components. | Yes |
| `state/` | Runtime live metric state. | Yes |
| `tabs/` | All workflow-specific code. | Yes |
| `utils/` | File validation, logging, memory helpers. | Yes |
| `visuals/` | Severity colors and dashboard summary generators. | Yes |
| `scripts/` | Developer/debug tooling, mainly VAMS matching validation. | No |
| `testcases/` | Regression/architecture tests. | No for runtime, yes for safe development |
| `docs/` | Detailed documentation. | No for runtime |

---

## Testing and validation

Run all tests:

```bash
python -m pytest -q
```

Compile-check all Python files:

```bash
python -m compileall -q .
```

The test suite verifies the tab-isolated architecture, dashboard layout contracts, UI contracts, output metric counting behavior, and important Excel dashboard behavior.
