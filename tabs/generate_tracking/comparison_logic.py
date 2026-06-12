"""Comparison and aggregation logic for raw/master scan datasets."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from tabs.generate_tracking.parser import TEMPLATE_COLUMNS, highest_risk, split_values

_KEY_ALIASES = {
    "Name": ("Name", "Title", "Vulnerability", "Plugin Name"),
    "Host / Image": ("Host / Image", "Host", "IP", "DNS", "Hostname", "Image"),
    "Port": ("Port", "Service Port", "TCP Port", "UDP Port"),
    "CVE": ("CVE", "CVE ID", "CVE IDs", "CVEs", "Vulnerability ID"),
}


def _normalized_column_name(value: object) -> str:
    return " ".join(str(value).strip().casefold().replace("_", " ").split())


def _series_for_key(df: pd.DataFrame, key_name: str) -> pd.Series:
    normalized_columns = {_normalized_column_name(column): column for column in df.columns}

    for alias in _KEY_ALIASES[key_name]:
        source_column = normalized_columns.get(_normalized_column_name(alias))
        if source_column is not None:
            return df[source_column].fillna("").astype(str).str.strip().str.casefold()

    return pd.Series([""] * len(df), index=df.index, dtype="object")


def _comparison_key(df: pd.DataFrame) -> pd.Series:
    key_parts = pd.DataFrame(
        {
            key_name: _series_for_key(df, key_name)
            for key_name in ("Name", "Host / Image", "Port", "CVE")
        },
        index=df.index,
    )
    return key_parts.agg("|".join, axis=1)


def merge_comma(values) -> str:
    """Merge repeated values into comma-separated, de-duplicated text."""
    merged = []

    for value in values:
        for token in split_values(value):
            if token not in merged:
                merged.append(token)

    return ", ".join(merged)


def classify_new_old(raw_df: pd.DataFrame, master_df: Optional[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split raw rows into New vs Old using tab-local Name+Host+Port+CVE logic.

    The Generate Tracking tab accepts both normalized scanner data and 3UK Qualys
    Total Vulnerabilities data, so the comparison key resolves common aliases
    such as Title/IP/CVE ID before comparing rows.
    """
    if master_df is None or master_df.empty:
        return raw_df.copy(), raw_df.iloc[0:0].copy()

    raw_keys = _comparison_key(raw_df)
    master_keys = set(_comparison_key(master_df))
    old_mask = raw_keys.isin(master_keys)
    return raw_df.loc[~old_mask].copy(), raw_df.loc[old_mask].copy()


def aggregate_unique(df: pd.DataFrame) -> pd.DataFrame:
    """Group by Name/CVE/Host and merge other fields with comma de-dup logic."""
    if df.empty:
        return pd.DataFrame(columns=TEMPLATE_COLUMNS)

    grouped_rows = []
    for _, group in df.groupby(["Name", "CVE", "Host / Image"], dropna=False, sort=False):
        row = {}
        for col in TEMPLATE_COLUMNS:
            if col == "Risk":
                row[col] = highest_risk(group[col].tolist())
            else:
                row[col] = merge_comma(group[col].tolist())
        grouped_rows.append(row)

    return pd.DataFrame(grouped_rows, columns=TEMPLATE_COLUMNS)
