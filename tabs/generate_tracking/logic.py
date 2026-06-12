"""Tab-local business logic boundary for Generate Tracking.

Keep tracking-specific comparison rules here so changes for this tab do not
spill into Make New Report or Add VAMS Data.
"""

from tabs.generate_tracking.comparison_logic import aggregate_unique, classify_new_old

__all__ = ["aggregate_unique", "classify_new_old"]
