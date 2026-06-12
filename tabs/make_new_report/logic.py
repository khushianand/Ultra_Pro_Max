"""Tab-local business logic boundary for Make New Report.

Keep Make New Report workflow rules here so future tab-specific changes do not
force Generate Tracking or Add VAMS Data to change.
"""

from tabs.make_new_report.comparison_logic import aggregate_unique

__all__ = ["aggregate_unique"]
