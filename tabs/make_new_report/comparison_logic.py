"""Comparison and aggregation logic for raw/master scan datasets."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from tabs.make_new_report.parser import TEMPLATE_COLUMNS, build_key, highest_risk, merge_semicolon


def classify_new_old(raw_df: pd.DataFrame, master_df: Optional[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split raw rows into New vs Old using key Name+Host+Port+CVE."""
    if master_df is None or master_df.empty:
        return raw_df.copy(), pd.DataFrame(columns=TEMPLATE_COLUMNS)

    raw_keys = build_key(raw_df, include_port=True)
    master_keys = set(build_key(master_df, include_port=True))
    old_mask = raw_keys.isin(master_keys)
    return raw_df.loc[~old_mask].copy(), raw_df.loc[old_mask].copy()


def aggregate_unique(df: pd.DataFrame) -> pd.DataFrame:
    """Group by Name/CVE/Host and merge all other fields with '; ' de-dup logic."""
    if df.empty:
        return pd.DataFrame(columns=TEMPLATE_COLUMNS)

    grouped_rows = []
    for _, group in df.groupby(["Name", "CVE", "Host / Image"], dropna=False, sort=False):
        row = {}
        for col in TEMPLATE_COLUMNS:
            if col == "Risk":
                row[col] = highest_risk(group[col].tolist())
            else:
                row[col] = merge_semicolon(group[col].tolist())
        grouped_rows.append(row)

    return pd.DataFrame(grouped_rows, columns=TEMPLATE_COLUMNS)
