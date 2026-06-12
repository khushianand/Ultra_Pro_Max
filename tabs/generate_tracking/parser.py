"""Parsing and normalization layer for scanner and VAMS Excel inputs.

Outputs DataFrames normalized to TEMPLATE_COLUMNS for downstream logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import pandas as pd

TEMPLATE_COLUMNS: List[str] = [
    "Scanner ID",
    "CVE",
    "CVSS v2.0 Base Score",
    "Risk",
    "Host / Image",
    "Protocol",
    "Port",
    "Name",
    "Synopsis",
    "Description",
    "Solution",
    "See Also",
    "Plugin Output",
    "CVSS v3.0 Base Score",
    "CVSS v3.0 Temporal Score",
    "Release Remediation Plan",
    "Release Remediation Date",
    "Expert Severity",
    "Expert Score",
    "Remediation Reference ID",
    "Disposition",
    "VAMS (PSL comments)",
    "MSS Comments",
]

REQUIRED_COLUMNS = [
    "Name",
    "Host / Image",
    "Port",
    "CVE",
    "Risk",
]

SEVERITY_PRIORITY = ["Critical", "High", "Medium", "Low"]
SEVERITY_ALLOWED = {s.lower() for s in SEVERITY_PRIORITY}

COLUMN_ALIASES: Dict[str, List[str]] = {
    "Scanner ID": [
        "plugin id",
        "plugin",
        "pluginid",
        "qid",
        "q id",
        "qid#",
        "scanner id",
    ],

    "CVE": [
        "cve",
        "cve id",
        "cve ids",
        "cves",
        "vulnerability id",
    ],

    "CVSS v2.0 Base Score": [
        "cvss",
        "cvss2",
        "cvss v2",
        "cvss v2.0 base score",
        "cvss base score",
        "reported cvss score",
    ],

    "Risk": [
        "risk",
        "risk factor",
        "severity",
        "threat",
        "vulnerability severity",
        "reported severity",
    ],

    "Host / Image": [
        "host",
        "ip",
        "ip address",
        "asset ip",
        "host / image",
        "host/image",
        "image",
        "package name",
        "host (ip address)",
        "dns",
        "hostname",
    ],

    "Protocol": [
        "protocol",
        "transport",
        "service protocol",
    ],

    "Port": [
        "port",
        "service port",
        "tcp port",
        "udp port",
        "interfaces",
    ],

    "Name": [
        "name",
        "title",
        "vulnerability",
        "plugin name",
        "vulnerability name",
    ],

    "Synopsis": [
        "synopsis",
        "summary",
        "threat",
        "package version",
    ],

    "Description": [
        "description",
        "details",
        "impact",
    ],

    "Solution": [
        "solution",
        "fix",
        "remediation",
        "status",
    ],

    "See Also": [
        "see also",
        "reference",
        "references",
        "url",
    ],

    "Plugin Output": [
        "plugin output",
        "output",
        "result",
        "evidence",
    ],

    "CVSS v3.0 Base Score": [
        "cvss3",
        "cvss3 base",
        "cvss v3",
        "cvss v3.0 base score",
        "reported cvss score",
    ],

    "CVSS v3.0 Temporal Score": [
        "cvss3 temporal",
        "cvss v3.0 temporal score",
        "cvss temporal",
        "expert cvss vector",
        "reported cvss vector",
    ],

    "Release Remediation Plan": [
        "release remediation plan",
    ],

    "Release Remediation Date": [
        "release remediation date",
    ],

    "Expert Severity": [
        "expert severity",
        "expert  severity",
    ],

    "Expert Score": [
        "expert score",
        "expert  score",
    ],

    "Remediation Reference ID": [
        "remediation reference id",
    ],

    "Disposition": [
        "disposition",
    ],

    "VAMS (PSL comments)": [
        "vams (psl comments)",
        "vams",
        "vams comments",
        "disposition rationale",
    ],

    "MSS Comments": [
        "mss comments",
        "mss",
        "customer guidance / mitigating controls",
    ],
}


@dataclass
class ParsedData:
    df: pd.DataFrame
    header_row: int


def norm_text(value: object) -> str:
    return " ".join(
        str(value)
        .strip()
        .lower()
        .replace("_", " ")
        .split()
    )


def split_values(value: object) -> List[str]:
    if value is None:
        return []

    text = str(value).replace("\n", ";")

    items: List[str] = []

    for chunk in text.split(";"):
        for part in chunk.split(","):
            cleaned = part.strip()

            if cleaned:
                items.append(cleaned)

    deduped: List[str] = []

    for item in items:
        if item not in deduped:
            deduped.append(item)

    return deduped


def merge_semicolon(values: Iterable[object]) -> str:
    merged: List[str] = []

    for value in values:
        for token in split_values(value):
            if token not in merged:
                merged.append(token)

    return "; ".join(merged)


def highest_risk(values: Iterable[object]) -> str:
    tokens = {
        v.lower()
        for v in split_values(merge_semicolon(values))
    }

    for sev in SEVERITY_PRIORITY:
        if sev.lower() in tokens:
            return sev

    return ""


def detect_header_row(path: str, sheet_name: str, scanner: str) -> int:
    preview = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=None,
        nrows=30,
    )

    keyword_groups = [
        {"ip", "ip address", "asset ip", "host", "host / image", "hostname"},
        {"qid", "q id", "plugin id", "scanner id"},
        {"severity", "risk", "vulnerability severity"},
        {"port", "service port", "tcp port", "udp port"},
        {"cve", "cve id", "cve ids"},
        {"name", "title", "vulnerability", "plugin name"},
    ]

    best_idx = 0
    best_score = -1

    for idx, row in preview.iterrows():
        row_norm = {
            norm_text(v)
            for v in row.tolist()
            if pd.notna(v)
        }

        score = 0

        for group in keyword_groups:
            if row_norm.intersection(group):
                score += 1

        if score >= 5:
            return int(idx)

        if score > best_score:
            best_score = score
            best_idx = int(idx)

    return best_idx


def _mapped_series(df: pd.DataFrame, target_col: str) -> pd.Series:
    normalized_columns = {
        norm_text(col): col
        for col in df.columns
    }

    for alias in COLUMN_ALIASES[target_col]:
        alias_norm = norm_text(alias)

        if alias_norm in normalized_columns:
            return df[normalized_columns[alias_norm]]

    if target_col == "CVE":
        for source_col in df.columns:
            if "cve" in norm_text(source_col):
                return df[source_col]

    return pd.Series([""] * len(df), index=df.index)


def normalize_columns(
    df: pd.DataFrame,
    apply_severity_filter: bool = True,
    preserve_source_columns: bool = False,
) -> pd.DataFrame:

    out = pd.DataFrame(index=df.index)

    for target in TEMPLATE_COLUMNS:
        out[target] = (
            _mapped_series(df, target)
            .fillna("")
            .astype(str)
            .str.strip()
        )

    for required in REQUIRED_COLUMNS:
        if required not in out.columns:
            out[required] = ""

    # Handle:
    # 123.123.123.123 (443)
    # -> Host / Image = 123.123.123.123
    # -> Port = 443

    host_series = (
        out["Host / Image"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    port_series = (
        out["Port"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    extracted_host = (
        host_series
        .str.replace(
            r"\s*\([^)]*\)\s*$",
            "",
            regex=True,
        )
        .str.strip()
    )

    extracted_port = (
        host_series
        .str.extract(r"\(([^)]*)\)", expand=False)
        .fillna("")
        .astype(str)
        .str.strip()
    )

    has_embedded = host_series.str.contains(
        r"\([^)]*\)",
        regex=True,
    )

    use_embedded_port = (
        has_embedded
        & (port_series == "")
        & (extracted_port != "")
    )

    out.loc[has_embedded, "Host / Image"] = extracted_host[has_embedded]

    out.loc[use_embedded_port, "Port"] = extracted_port[use_embedded_port]

    if preserve_source_columns:
        source_values = {}

        for source_col in df.columns:
            source_col_name = str(source_col)

            if source_col_name not in out.columns:
                source_values[source_col_name] = (
                    df[source_col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        if source_values:
            out = pd.concat(
                [
                    out,
                    pd.DataFrame(source_values, index=df.index),
                ],
                axis=1,
            )

    if apply_severity_filter:
        out = filter_severity(out)

    output_columns = TEMPLATE_COLUMNS + [
        col
        for col in out.columns
        if col not in TEMPLATE_COLUMNS
    ]

    return out[output_columns].reset_index(drop=True)


def parse_scan_file(
    path: str,
    sheet_name: str,
    scanner: str,
    project: str,
    require_rows_after_filter: bool = True,
    apply_severity_filter: bool = True,
) -> ParsedData:

    header_row = detect_header_row(
        path,
        sheet_name,
        scanner,
    )

    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=header_row,
    )

    if df.empty:
        raise ValueError("Input sheet is empty")

    preserve_source_columns = (
    project.strip().casefold() == "3uk"
    and scanner.strip().casefold() == "qualys"
)

    # ---------------------------------------------------------
# SPECIAL FLOW:
# 3UK + QUALYS
# KEEP RAW DATAFRAME
# ---------------------------------------------------------

    
    # ---------------------------------------------------------
    # NORMAL FLOW
    # ---------------------------------------------------------
    
    parsed = normalize_columns(
        df,
        apply_severity_filter=apply_severity_filter,
        preserve_source_columns=preserve_source_columns,
    )
    
    if require_rows_after_filter and parsed.empty:
        raise ValueError("No rows left after severity filtering")
    
    return ParsedData(
        df=parsed,
        header_row=header_row,
    )


def filter_severity(df: pd.DataFrame) -> pd.DataFrame:
    risk = (
        df["Risk"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    normalized = (
        risk
        .str.extract(
            r"(critical|high|medium|low|[1-4])",
            expand=False,
        )
        .replace({
            "1": "low",
            "2": "medium",
            "3": "high",
            "4": "critical",
        })
        .fillna("")
    )

    df_out = df.copy()

    df_out["Risk"] = normalized.str.title()

    return df_out.loc[
        normalized.isin(SEVERITY_ALLOWED)
    ].copy()


def build_key(
    df: pd.DataFrame,
    include_port: bool = True,
) -> pd.Series:

    fields = (
        ["Name", "Host / Image", "Port", "CVE"]
        if include_port
        else ["Name", "Host / Image", "CVE"]
    )

    return (
        df[fields]
        .fillna("")
        .astype(str)
        .apply(
            lambda c: c.str.strip().str.lower(),
            axis=0,
        )
        .agg("|".join, axis=1)
    )
