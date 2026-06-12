"""Summary table generators used by dashboard sheets and charts."""

from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd

SEVERITY_ORDER: Dict[str, str] = {
    "Critical": "#9B0F06",
    "High": "#D53E0F",
    "Medium": "#F77F00",
    "Low": "#FCBF49",
}
SUMMARY_VALUE_COLUMN = " "  # Blank value header keeps chart labels numeric without showing extra text.


def _normalized_series(df: pd.DataFrame, column: str) -> pd.Series:
    return df.get(column, pd.Series(dtype=str)).fillna("").astype(str).str.strip()


def _severity_counts(df: pd.DataFrame) -> List[Dict[str, object]]:
    risk = _normalized_series(df, "Risk").str.lower()
    return [
        {"Severity": severity, SUMMARY_VALUE_COLUMN: int((risk == severity.lower()).sum())}
        for severity in SEVERITY_ORDER
    ]


def severity_summary(df: pd.DataFrame) -> pd.DataFrame:
    counts = _severity_counts(df)
    counts.append({"Severity": "Total", SUMMARY_VALUE_COLUMN: sum(int(item[SUMMARY_VALUE_COLUMN]) for item in counts)})
    return pd.DataFrame(counts)


def severity_chart_summary(df: pd.DataFrame, include_total: bool = True) -> pd.DataFrame:
    """Return severity counts for dashboard chart data sources."""
    summary_df = pd.DataFrame(_severity_counts(df))
    if include_total:
        summary_df = pd.concat(
            [
                summary_df,
                pd.DataFrame(
                    {
                        "Severity": ["Total"],
                        SUMMARY_VALUE_COLUMN: [int(summary_df[SUMMARY_VALUE_COLUMN].sum())],
                    }
                ),
            ],
            ignore_index=True,
        )
    return summary_df


def expert_severity_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return reported vs expert severity counts for the VAMS dashboard bar chart."""
    reported = _normalized_series(df, "Risk").str.lower()
    expert = _normalized_series(df, "Expert Severity").str.lower()
    return pd.DataFrame(
        {
            "Severity": severity,
            "Reported": int((reported == severity.lower()).sum()),
            "Expert": int((expert == severity.lower()).sum()),
        }
        for severity in SEVERITY_ORDER
    )


def _split_summary_values(value: object) -> List[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"\s*;\s*", text) if part.strip()]


def disposition_summary(df: pd.DataFrame, disposition_order: List[str]) -> pd.DataFrame:
    """Return disposition counts, including semicolon-merged VAMS values."""
    normalized_order = {value.lower(): value for value in disposition_order}
    counts = {value: 0 for value in disposition_order}
    for value in _normalized_series(df, "Disposition"):
        for token in _split_summary_values(value):
            display = normalized_order.get(token.lower(), token)
            counts[display] = counts.get(display, 0) + 1
    return pd.DataFrame({"Disposition": key, SUMMARY_VALUE_COLUMN: int(value)} for key, value in counts.items())
