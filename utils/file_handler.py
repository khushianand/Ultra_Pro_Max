"""File validation and Excel sheet-discovery helpers."""

from pathlib import Path
from typing import List

import pandas as pd


def validate_file(path: str) -> None:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.suffix.lower() not in {".xlsx", ".xlsm", ".xls"}:
        raise ValueError(f"Unsupported file format: {path}")


def list_excel_sheets(path: str) -> List[str]:
    validate_file(path)
    return pd.ExcelFile(path).sheet_names
