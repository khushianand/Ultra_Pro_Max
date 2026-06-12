"""Tab-local business constants for Add VAMS Data."""

from tabs.add_vams_data.vams_enrichment import VAMS_COLUMNS

TOTAL_SHEET_CANDIDATES = (
    "Total Vulnerabilities",
    "Total vulnerabilities",
    "Total Data",
    "New Data",
    "Total Vulnerability",
)

UNIQUE_SHEET_CANDIDATES = (
    "Unique Vulnerabilities",
    "Unique Data",
)

__all__ = ["TOTAL_SHEET_CANDIDATES", "UNIQUE_SHEET_CANDIDATES", "VAMS_COLUMNS"]
