"""Tab-local business logic boundary for Generate Tracking.

Keep tracking-specific comparison rules here so changes for this tab do not
spill into Make New Report or Add VAMS Data.
"""

from tabs.generate_tracking.comparison_logic import (
    aggregate_unique,
    build_comparison_debug_df,
    build_template_sheet_df,
    classify_new_old,
    comparison_non_empty_counts,
    comparison_values_preview,
    resolve_comparison_columns,
)

__all__ = [
    "aggregate_unique",
    "build_comparison_debug_df",
    "build_template_sheet_df",
    "classify_new_old",
    "comparison_non_empty_counts",
    "comparison_values_preview",
    "resolve_comparison_columns",
]
