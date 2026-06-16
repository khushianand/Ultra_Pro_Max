"""Comparison and aggregation logic for raw/master scan datasets."""

from __future__ import annotations

import re
from typing import Optional

import pandas as pd

from tabs.generate_tracking.parser import COLUMN_ALIASES, TEMPLATE_COLUMNS, highest_risk, split_values

_KEY_ALIASES = {
    "Name": ("Name", "Title", "Vulnerability", "Plugin Name"),
    "Host / Image": ("Host / Image", "Host", "IP", "DNS", "Hostname", "Image"),
    "Port": ("Port", "Service Port", "TCP Port", "UDP Port"),
    "CVE": ("CVE", "CVE ID", "CVE IDs", "CVEs", "Vulnerability ID"),
}


def _normalized_column_name(value: object) -> str:
    return " ".join(str(value).strip().casefold().replace("_", " ").split())


def normalize_key_value(value: object) -> str:
    """Normalize one comparison-key value for null-safe matching."""
    if pd.isna(value):
        return ""

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    text = str(value).strip().casefold()
    if re.fullmatch(r"\d+\.0+", text):
        return text.split(".", 1)[0]

    return text


def find_column(df: pd.DataFrame, aliases) -> str | None:
    """Return the first DataFrame column matching any alias, case/spacing safe."""
    normalized_columns = {_normalized_column_name(column): column for column in df.columns}

    for alias in aliases:
        source_column = normalized_columns.get(_normalized_column_name(alias))
        if source_column is not None:
            return source_column

    return None


def _series_for_key(df: pd.DataFrame, key_name: str) -> pd.Series:
    source_column = find_column(df, _KEY_ALIASES[key_name])
    if source_column is not None:
        return df[source_column].map(normalize_key_value).astype("object")

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


def _aliases_for_template_column(target_col: str) -> tuple[str, ...]:
    aliases = [target_col]
    aliases.extend(_KEY_ALIASES.get(target_col, ()))
    aliases.extend(COLUMN_ALIASES.get(target_col, ()))
    return tuple(dict.fromkeys(aliases))


def _alias_series_for_output(df: pd.DataFrame, target_col: str) -> pd.Series:
    source_column = find_column(df, _aliases_for_template_column(target_col))
    if source_column is not None:
        return df[source_column]
    return pd.Series([""] * len(df), index=df.index, dtype="object")


def build_template_sheet_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return Raw-derived rows in universal template-column order."""
    out = pd.DataFrame(index=df.index)
    for col in TEMPLATE_COLUMNS:
        out[col] = _alias_series_for_output(df, col).fillna("").astype(str).str.strip()
    return out[TEMPLATE_COLUMNS].reset_index(drop=True)


def _template_view(df: pd.DataFrame) -> pd.DataFrame:
    return build_template_sheet_df(df)


def resolve_comparison_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """Resolve the actual DataFrame columns used for comparison fields."""
    return {
        key_name: find_column(df, _KEY_ALIASES[key_name])
        for key_name in ("Name", "Host / Image", "Port", "CVE")
    }


def comparison_non_empty_counts(df: pd.DataFrame, resolved_columns: dict[str, str | None]) -> dict[str, int]:
    """Count non-empty values for each resolved comparison column."""
    counts = {}
    for key_name, column in resolved_columns.items():
        if column is None:
            counts[key_name] = 0
            continue
        counts[key_name] = int(df[column].fillna("").astype(str).str.strip().ne("").sum())
    return counts


def _comparison_values_df(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Name": _series_for_key(df, "Name"),
            "Host / Image": _series_for_key(df, "Host / Image"),
            "Port": _series_for_key(df, "Port"),
            "CVE": _series_for_key(df, "CVE"),
        },
        index=df.index,
    )


def comparison_values_preview(df: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    """Show the normalized values that will be used to build comparison keys."""
    return _comparison_values_df(df).head(limit)


def build_comparison_debug_df(raw_df: pd.DataFrame, master_df: pd.DataFrame) -> pd.DataFrame:
    """Build a Raw-side comparison debug sheet with generated key match status."""
    raw_values = _comparison_values_df(raw_df)
    raw_keys = raw_values.agg("|".join, axis=1)
    blank_key = "|||"
    master_keys = {
        key
        for key in _comparison_key(master_df)
        if key != blank_key
    }

    return pd.DataFrame(
        {
            "Raw Name": raw_values["Name"],
            "Raw Host / Image": raw_values["Host / Image"],
            "Raw Port": raw_values["Port"],
            "Raw CVE": raw_values["CVE"],
            "Generated Key": raw_keys,
            "Match Status": [
                "Matched" if key != blank_key and key in master_keys else "Unmatched"
                for key in raw_keys
            ],
        }
    )


def classify_new_old(raw_df: pd.DataFrame, master_df: Optional[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split raw rows into New vs Old using tab-local Name+Host+Port+CVE logic.

    The Generate Tracking tab accepts both normalized scanner data and 3UK Qualys
    Total Vulnerabilities data, so the comparison key resolves common aliases
    such as Title/IP/CVE ID before comparing rows.
    """
    if master_df is None or master_df.empty:
        return raw_df.copy(), raw_df.iloc[0:0].copy()

    raw_keys = _comparison_key(raw_df)
    blank_key = "|||"
    master_keys = {
        key
        for key in _comparison_key(master_df)
        if key != blank_key
    }
    old_mask = raw_keys.ne(blank_key) & raw_keys.isin(master_keys)
    return raw_df.loc[~old_mask].copy(), raw_df.loc[old_mask].copy()


def aggregate_unique(df: pd.DataFrame) -> pd.DataFrame:
    """Group raw findings by Name/CVE/Host and merge all template fields."""
    if df.empty:
        return pd.DataFrame(columns=TEMPLATE_COLUMNS)

    template_df = _template_view(df)
    grouped_rows = []
    for _, group in template_df.groupby(["Name", "CVE", "Host / Image"], dropna=False, sort=False):
        row = {}
        for col in TEMPLATE_COLUMNS:
            if col == "Risk":
                row[col] = highest_risk(group[col].tolist())
            else:
                row[col] = merge_comma(group[col].tolist())
        grouped_rows.append(row)

    return pd.DataFrame(grouped_rows, columns=TEMPLATE_COLUMNS)
