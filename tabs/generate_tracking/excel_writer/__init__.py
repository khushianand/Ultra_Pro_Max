"""Backward-compatible public exports for Excel output helpers.

Implementation is split across focused package modules:
- ``workbook``: workbook creation and sheet ordering
- ``reader``: loading generated workbook sheets into DataFrames
- ``sheets``: individual sheet writers
- ``formatting``: reusable styles and layout helpers
- ``three_uk_qualys``: 3UK + Qualys Total Data mapping
"""

from __future__ import annotations

from tabs.generate_tracking.excel_writer.reader import read_sheet_as_df
from tabs.generate_tracking.excel_writer.sheets import write_disposition_sheet, write_main_sheet, write_summary_sheet
from tabs.generate_tracking.excel_writer.workbook import write_output
from tabs.generate_tracking.excel_writer.three_uk_qualys import (
    THREE_UK_QUALYS_TOTAL_COLUMNS,
    build_3uk_qualys_template_sheet_df,
    build_3uk_qualys_total_sheet_df,
    build_3uk_qualys_unique_sheet_df,
)

__all__ = [
    "THREE_UK_QUALYS_TOTAL_COLUMNS",
    "build_3uk_qualys_template_sheet_df",
    "build_3uk_qualys_total_sheet_df",
    "build_3uk_qualys_unique_sheet_df",
    "read_sheet_as_df",
    "write_disposition_sheet",
    "write_main_sheet",
    "write_output",
    "write_summary_sheet",
]
