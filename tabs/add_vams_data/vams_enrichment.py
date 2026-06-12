"""Dedicated VAMS enrichment engine.

This module maps VAMS rows into:
- New Data: fill-only VAMS-managed fields after key match (no overwrite)
- Unique Data: merge-only VAMS-managed fields (no overwrite)
"""

from __future__ import annotations

import re
import pandas as pd

from tabs.add_vams_data.parser import merge_semicolon, split_values
from tabs.add_vams_data.fast_vams_enrichment import FastVamsEnrichmentEngine


VAMS_COLUMNS = [
    "Release Remediation Plan",
    "Release Remediation Date",
    "Expert Severity",
    "Expert Score",
    "Remediation Reference ID",
    "Disposition",
    "VAMS (PSL comments)",
    "MSS Comments",
]


def _norm(value: object) -> str:
    return str(value).strip().lower()

def _split_multi_values(value):

    if value is None:
        return []

    value = str(value).strip()

    if not value:
        return []

    return [

        _norm(v)

        for v in re.split(
            r"[;,]",
            value,
        )

        if str(v).strip()
    ]


def _extract_host_and_ports(value):

    """
    Handles:
        10.0.0.1
        10.0.0.1 (443)
        host.com (8443)
    """

    if value is None:
        return [""]

    raw = str(value).strip()

    embedded_ports = re.findall(
        r"\((.*?)\)",
        raw,
    )

    host_clean = re.sub(
        r"\s*\(.*?\)",
        "",
        raw,
    ).strip()

    hosts = [

        _norm(h)

        for h in re.split(
            r"[;,]",
            host_clean,
        )

        if h.strip()
    ]

    if not hosts:
        hosts = [""]

    return hosts, embedded_ports


def _is_numeric_like(value):

    if not value:
        return False

    return str(value).strip().isdigit()

def _norm_port(value: object) -> str:
    token = _norm(value)

    if re.match(r"^\d+\.0+$", token):
        return token.split(".", 1)[0]

    return token


def _fallback_cve_tokens(row: pd.Series) -> list[str]:

    raw_cve_tokens = split_values(row.get("CVE", ""))

    normalized: list[str] = []

    for token in raw_cve_tokens:

        t = str(token).strip()

        if not t:
            continue

        if re.match(r"(?i)^cve-\d{4}-\d+$", t):
            normalized.append(t.lower())
            continue

        normalized.extend(re.findall(r"\d+", t))

    if normalized:
        return normalized

    plugin_tokens = re.findall(
        r"\d+",
        str(
            row.get(
                "Scanner ID",
                row.get("Plugin ID", ""),
            )
        ),
    )

    return plugin_tokens


def _extract_port_tokens(value: object) -> list[str]:
    """
    Extract port tokens including:
    443
    80;443
    1.1.1.1 (443)
    """

    text = str(value or "").strip()

    if not text:
        return []

    bracket_tokens = re.findall(r"\(([^)]*)\)", text)

    parsed = split_values(
        ";".join(bracket_tokens)
        if bracket_tokens
        else text
    )

    return parsed or ([text] if text else [])


def _extract_host_and_embedded_ports(
    value: object,
) -> tuple[str, list[str]]:

    """
    Parse:
    1.1.1.1 (443)

    into:

    host = 1.1.1.1
    ports = ['443']
    """

    text = str(value or "").strip()

    if not text:
        return "", []

    ip_or_host = re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        text,
    ).strip()

    embedded_ports = re.findall(
        r"\(([^)]*)\)",
        text,
    )

    ports = (
        split_values(";".join(embedded_ports))
        if embedded_ports
        else []
    )

    return ip_or_host, ports


def _row_keys(
    row: pd.Series,
    include_port: bool,
) -> set[str]:

    name = _norm(row.get("Name", ""))

    host_value = row.get("Host / Image", "")

    if (
        not str(host_value).strip()
        or str(host_value).lower() == "nan"
    ):
        host_value = row.get("Host", "")

    parsed_host, embedded_ports = (
        _extract_host_and_embedded_ports(host_value)
    )

    hosts = (
        split_values(parsed_host)
        or ([parsed_host] if parsed_host else [])
        or split_values(host_value)
        or [host_value]
    )

    cves = (
        _fallback_cve_tokens(row)
        or [row.get("CVE", "")]
    )

    if include_port:

        ports = (
            _extract_port_tokens(row.get("Port", ""))
            or embedded_ports
            or [row.get("Port", "")]
        )

        return {
            f"{name}|{_norm(h)}|{_norm_port(p)}|{_norm(c)}"
            for h in hosts
            for p in ports
            for c in cves
        }

    return {
        f"{name}|{_norm(h)}|{_norm(c)}"
        for h in hosts
        for c in cves
    }


def _value_in_merged_cell(
    target: str,
    merged_cell: str,
) -> bool:

    target_tokens = {
        _norm_port(token)
        for token in split_values(target)
    }

    merged_tokens = {
        _norm_port(token)
        for token in split_values(merged_cell)
    }

    return bool(target_tokens.intersection(merged_tokens))


def enrich_with_vams(
    new_df: pd.DataFrame,
    unique_df: pd.DataFrame,
    vams_df: pd.DataFrame,
    *,
    new_data_match_include_port: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    """
    Apply VAMS fields into output dataframes
    with robust matching.
    """

    if vams_df.empty:
        return new_df, unique_df

    engine = FastVamsEnrichmentEngine()
    engine.build_vams_lookup(vams_df)

    # New and Unique now share the same fast matching logic:
    # Name + CVE(+fallback Plugin/Scanner ID) + Host + Port
    # with host embedded-port regex support and no-overwrite behavior.
    out_new = engine.enrich(new_df.copy())
    out_unique = engine.enrich(unique_df.copy())

    return out_new, out_unique


def update_vams_existing_workbook(
    new_df: pd.DataFrame,
    unique_df: pd.DataFrame,
    incoming_vams_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    return enrich_with_vams(
        new_df,
        unique_df,
        incoming_vams_df,
        new_data_match_include_port=True,
    )
