# All Definitions, Sequence, and Structure

This document maps the current Python structure and the high-level sequence of important definitions. It intentionally avoids fragile line numbers; use the file paths and function/class names below when navigating the code.

---

## 1. Runtime sequence

```text
main.py
  App.__init__
  App.show_window1
    Window1Entry
  App.show_window2
    Window2ProjectSelection
  App.show_window3
    Window3ScannerSelection
  App.show_window4
    Window4Main
      SummaryCards
      WorkflowStepper
      CTkTabview
        MakeNewReportTab
        GenerateTrackingTab
        AddVamsDataTab
        Show Summary tab
      LogsPanel
```

---

## 2. Root definitions

### `main.py`

- `class App`
- `App.__init__`
- `App._configure_styles`
- `App.toggle_theme_mode`
- `App._swap`
- `App.show_window1`
- `App.show_window2`
- `App.show_window3`
- `App.show_window4`

---

## 3. GUI definitions

### Wizard files

`gui/window1_entry.py`

- `class Window1Entry`
- builds entry mode selection and stores `entry_mode`

`gui/window2_project_selection.py`

- `class Window2ProjectSelection`
- builds project selector and stores `selected_project`

`gui/window3_scanner_selection.py`

- `class Window3ScannerSelection`
- builds scanner selector and stores `selected_scanner`

### Dashboard file

`gui/window4_main.py`

- `class Window4Main`
- `Window4Main._build`
- `Window4Main._build_summary_tab`
- `Window4Main._on_tab_change`
- `Window4Main._on_nav`
- `Window4Main._apply_window_background`
- `Window4Main._toggle_theme`
- `Window4Main._current_output_path`
- `Window4Main._open_output_file`
- `Window4Main._open_summary_dashboard`
- `Window4Main._open_settings_modal`
- `Window4Main._export_logs`
- `Window4Main._reset_current_tab`
- `Window4Main._schedule_timer_tick`
- `Window4Main._timer_tick`
- `Window4Main._normalized_excel_name`
- `Window4Main._find_workbook_sheet`
- `Window4Main._count_sheet_name_entries`
- `Window4Main._refresh_output_metrics`
- `Window4Main.set_run_state`
- `Window4Main.set_stage`
- `Window4Main.update_metrics`
- `Window4Main.attach_log_handler`
- `Window4Main.append_log`

---

## 4. GUI UI component definitions

### `gui/ui/cards.py`

- `class SummaryCards`
- `SummaryCards.__init__`
- `SummaryCards.update_metrics`

Stores four card values and dynamic tag labels:

- Vulnerabilities Processed → Total sheet count
- Unique Vulnerabilities → Unique sheet count
- Processing Time → elapsed time
- Success Rate → completion percent

### `gui/ui/header.py`

- `class HeaderPanel`

### `gui/ui/logs_panel.py`

- `class LogsPanel`
- log append/search/open-output UI support

### `gui/ui/sidebar.py`

- `class Sidebar`

### `gui/ui/themes.py`

- `palette(theme_name)`

### `gui/ui/workflow_stepper.py`

- `class WorkflowStepper`
- stage update methods

---

## 5. State definitions

### `state/app_state.py`

- `class LiveMetrics`
- `LiveMetrics.subscribe`
- `LiveMetrics.notify`
- `LiveMetrics.reset`
- `LiveMetrics.start`
- `LiveMetrics.tick`
- `LiveMetrics.stop`

---

## 6. Workflow tab definitions

## 6.1 Make Report

### `tabs/make_new_report/make_new_report.py`

- `class MakeNewReportTab`
- `__init__`
- `_build_ui`
- `_browse_raw`
- `_browse_output`
- `_validate_inputs`
- `run`
- `reset`

### `tabs/make_new_report/logic.py`

- Exports `aggregate_unique`

### `tabs/make_new_report/comparison_logic.py`

- `classify_new_old`
- `aggregate_unique`

### `tabs/make_new_report/parser.py`

- `class ParsedData`
- `norm_text`
- `split_values`
- `merge_semicolon`
- `highest_risk`
- `detect_header_row`
- `_mapped_series`
- `normalize_columns`
- `parse_scan_file`
- `filter_severity`
- `build_key`

## 6.2 Generate Tracking

### `tabs/generate_tracking/generate_tracking.py`

- `class GenerateTrackingTab`
- `__init__`
- `_build_ui`
- `_file_row`
- `_bind_validation`
- `_validate_form`
- `_load_sheets`
- `_browse_master`
- `_browse_raw`
- `_browse_output`
- `_validate_inputs`
- `_parse_with_optional_severity_fallback`
- `run`
- `reset`

### `tabs/generate_tracking/logic.py`

- Exports `aggregate_unique`
- Exports `classify_new_old`

### `tabs/generate_tracking/comparison_logic.py`

- `classify_new_old`
- `aggregate_unique`

### `tabs/generate_tracking/parser.py`

- `class ParsedData`
- `norm_text`
- `split_values`
- `merge_semicolon`
- `highest_risk`
- `detect_header_row`
- `_mapped_series`
- `normalize_columns`
- `parse_scan_file`
- `filter_severity`
- `build_key`

## 6.3 Add VAMS Data

### `tabs/add_vams_data/add_vams_data.py`

- `class AddVamsDataTab`
- `__init__`
- `_build`
- `_file_row`
- `_bind_validation`
- `_update_run_state`
- `_browse_output`
- `_browse_raw`
- `_validate_inputs`
- `_read_generated_sheet`
- `_write_vams_columns_only`
- `_refresh_dashboard_charts`
- `run`
- `reset`

### `tabs/add_vams_data/logic.py`

- `TOTAL_SHEET_CANDIDATES`
- `UNIQUE_SHEET_CANDIDATES`
- `VAMS_COLUMNS`

### `tabs/add_vams_data/parser.py`

- `class ParsedData`
- `norm_text`
- `split_values`
- `merge_semicolon`
- `highest_risk`
- `detect_header_row`
- `_mapped_series`
- `normalize_columns`
- `parse_scan_file`
- `filter_severity`
- `build_key`

### `tabs/add_vams_data/fast_vams_enrichment.py`

- `_norm`
- `_split_multi_values`
- `_extract_host_and_ports`
- `_is_numeric_like`
- `_is_empty`
- `build_fast_keys`
- `class FastVamsEnrichmentEngine`
- `FastVamsEnrichmentEngine.__init__`
- `FastVamsEnrichmentEngine.build_vams_lookup`
- `FastVamsEnrichmentEngine.enrich`

### `tabs/add_vams_data/vams_enrichment.py`

- `_norm`
- `_split_multi_values`
- `_extract_host_and_ports`
- `_is_numeric_like`
- `_norm_port`
- `_fallback_cve_tokens`
- `_extract_port_tokens`
- `_extract_host_and_embedded_ports`
- `_row_keys`
- `_value_in_merged_cell`
- `enrich_with_vams`
- `update_vams_existing_workbook`

---

## 7. Excel writer definitions

Each workflow owns this same local package pattern:

```text
tabs/<workflow>/excel_writer/
  __init__.py
  formatting.py
  reader.py
  sheets.py
  three_uk_qualys.py
  workbook.py
```

### `excel_writer/__init__.py`

Exports local writer functions and 3UK Qualys builders, including:

- `write_output`
- `write_main_sheet`
- `write_summary_sheet`
- `write_disposition_sheet`
- `read_sheet_as_df`
- `apply_table_formatting`
- `build_3uk_qualys_total_sheet_df`
- `build_3uk_qualys_unique_sheet_df`

### `excel_writer/formatting.py`

Common definitions in each tab package:

- `thin_border`
- `fill`
- `font`
- `style_meta_row`
- `write_headers`
- `write_summary_headers`
- `apply_table_formatting`
- `auto_width`

### `excel_writer/reader.py`

- `_normalized_header`
- `_fill_from_display_alias`
- `read_sheet_as_df`

### `excel_writer/sheets.py`

- `_write_data_rows`
- `write_main_sheet`
- `_clear_dashboard`
- `_hide_chart_source_columns`
- `_write_chart_source`
- `_color_series_points`
- `_add_pie`
- `_add_bar`
- `_append_pie_charts`
- `_append_vams_bar_charts`
- `write_summary_sheet`
- `write_disposition_sheet`

### `excel_writer/three_uk_qualys.py`

- `is_three_uk_qualys_project`
- `detect_qualys_header_row`
- `severity_to_criticality`
- `criticality_series`
- `map_risk`
- `three_uk_qualys_total_view`
- `build_3uk_qualys_total_sheet_df`
- `build_3uk_vams_matching_df`
- `build_3uk_qualys_unique_sheet_df`
- `merge_semicolon_separated`

### `excel_writer/workbook.py`

- `_normalized_sheet_name`
- `normalize_total_sheet_name`
- `autofit_worksheet_columns`
- `write_output`

---

## 8. Visual definitions

### `visuals/highlight_logic.py`

- `severity_fill`

### `visuals/summary/summary_generator.py`

- `_normalized_series`
- `_severity_counts`
- `severity_summary`
- `severity_chart_summary`
- `expert_severity_summary`
- `_split_summary_values`
- `disposition_summary`

### `visuals/summary/summary_update_logic.py`

- Exposes summary/dashboard refresh writer from the Add VAMS Data local Excel writer.

---

## 9. Utility definitions

### `utils/file_handler.py`

- `validate_file`
- `list_excel_sheets`

### `utils/logger.py`

- `get_logger`
- `class UILogHandler`
- `UILogHandler.emit`

### `utils/memory.py`

- `memory_session`
- `release_large_objects`

---

## 10. Script definitions

### `scripts/validate_vams_enrichment.py`

- `_pick_sheet`
- `_safe`
- `_preview_row`
- `debug_match`
- `debug_vams_quality`
- `main`

---

## 11. Test definitions

### `testcases/validation_engine.py`

- `load_all_tests`

### `testcases/test_summary/test_architecture_contracts.py`

Architecture contract tests for required files, tab-owned layout, removed root `logic/`, and imports.

### `testcases/test_summary/test_dashboard_layout.py`

Excel Dashboard layout and chart contract tests.

### `testcases/test_summary/test_ui_contracts.py`

Dashboard UI, Show Summary, reset, logs, metric cards, and output count contract tests.

---

## 12. Critical sequence summaries

### Make Report sequence

```text
MakeNewReportTab.run
  → validate_file/list_excel_sheets
  → parser.parse_scan_file OR 3UK Qualys builders
  → aggregate_unique
  → excel_writer.write_output
  → apply_table_formatting
  → ui_hooks.set_run_state("Success")
```

### Generate Tracking sequence

```text
GenerateTrackingTab.run
  → validate inputs
  → parse raw data
  → parse required master data
  → classify_new_old
  → aggregate_unique
  → write_output(new_df, old_df, unique_df)
  → Total Vulnerabilities receives new_df
```

### Add VAMS Data sequence

```text
AddVamsDataTab.run
  → validate inputs
  → read generated sheets
  → parse VAMS file
  → FastVamsEnrichmentEngine.build_vams_lookup
  → enrich Total/Unique
  → _write_vams_columns_only
  → _refresh_dashboard_charts
  → save workbook
```

### Dashboard metric sequence

```text
Tab calls ui_hooks.set_run_state("Running")
  → LiveMetrics.start
  → timer tick updates Processing Time
  → tab calls ui_hooks.set_stage(...)
  → Success Rate progresses
  → tab calls ui_hooks.set_run_state("Success")
  → Window4Main counts output sheet Name entries
  → LiveMetrics.stop(success=True)
  → SummaryCards update values and tag labels
```
