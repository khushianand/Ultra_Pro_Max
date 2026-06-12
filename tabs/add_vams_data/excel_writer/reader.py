"""Excel input helpers for previously generated output workbooks."""

from __future__ import annotations

import pandas as pd

from tabs.add_vams_data.parser import TEMPLATE_COLUMNS
DISPLAY_COLUMN_ALIASES = {
    "Scanner ID": ["QID", "Plugin ID"],
    "CVE": ["CVE ID"],
    "CVSS v3.0 Base Score": ["CVSS3 Base", "CVSS Base", "CVSS"],
    "Risk": ["Severity"],
    "Host / Image": ["IP", "Host"],
    "Name": ["Title"],
    "Synopsis": ["Threat"],
    "Description": ["Impact"],
    "Plugin Output": ["Results"],
    "CVSS v3.0 Temporal Score": ["CVSS3 Temporal", "CVSS Temporal"],
}


def _normalized_header(value: object) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").split())


def _fill_from_display_alias(df: pd.DataFrame, target_col: str):
    normalized_columns = {_normalized_header(col): col for col in df.columns}
    actual_target = normalized_columns.get(_normalized_header(target_col))
    if actual_target is not None and df[actual_target].fillna("").astype(str).str.strip().ne("").any():
        if actual_target != target_col:
            df[target_col] = df[actual_target]
        return

    for alias in DISPLAY_COLUMN_ALIASES.get(target_col, []):
        actual_alias = normalized_columns.get(_normalized_header(alias))
        if actual_alias is not None:
            df[target_col] = df[actual_alias]
            return



def read_sheet_as_df(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name, header=1)
    for col in TEMPLATE_COLUMNS:
        _fill_from_display_alias(df, col)        
        if col not in df.columns:
            df[col] = ""
    return df[TEMPLATE_COLUMNS].fillna("")
