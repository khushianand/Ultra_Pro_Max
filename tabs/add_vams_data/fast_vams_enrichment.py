from __future__ import annotations

import re
import pandas as pd

from tabs.add_vams_data.parser import merge_semicolon, split_values


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


# ---------------------------------------------------------
# NORMALIZATION HELPERS
# ---------------------------------------------------------

def _norm(value: object) -> str:
    """Standardizes strings for matching: stripped and lowercase."""
    return str(value).strip().lower()

def _split_multi_values(value):

    """
    Split:
        a;b,c

    into normalized list.
    """

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
        host1;host2

    Returns:
        hosts,
        embedded_ports
    """

    if value is None:

        return [""] , []

    raw = str(value).strip()

    # ---------------------------------------------
    # Extract ports inside parentheses
    # ---------------------------------------------

    embedded_ports = re.findall(
        r"\((.*?)\)",
        raw,
    )

    # ---------------------------------------------
    # Remove:
    # (443)
    # ---------------------------------------------

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

    """
    Check if value looks numeric.
    Used for:
        CVE column containing
        Scanner ID digits.
    """

    if value is None:
        return False

    value = str(value).strip()

    if not value:
        return False

    return value.isdigit()

def _is_empty(value: str) -> bool:
    """Checks if a cell is essentially empty or a placeholder."""
    val = str(value).strip().lower()
    return not val or val == "nan"


# ---------------------------------------------------------
# FAST KEY BUILDER
# ---------------------------------------------------------

def build_fast_keys(
    df: pd.DataFrame,
) -> list[list[dict]]:

    """
    Enterprise tiered matching keys.
    """

    all_rows = []

    for _, row in df.iterrows():

        name = _norm(
            row.get(
                "Name",
                "",
            )
        )

        # -------------------------------------------------
        # HOSTS
        # -------------------------------------------------

        hosts, embedded_ports = (
            _extract_host_and_ports(

                row.get(

                    "Host / Image",

                    row.get(

                        "Host",

                        row.get(
                            "IP",
                            "",
                        ),
                    ),
                )
            )
        )

        # -------------------------------------------------
        # PORTS
        # -------------------------------------------------

        ports = _split_multi_values(
            row.get(
                "Port",
                "",
            )
        )

        ports.extend(

            _norm(p)

            for p in embedded_ports
            if p.strip()
        )

        ports = list(
            dict.fromkeys(ports)
        )

        if not ports:
            ports = [""]

        # -------------------------------------------------
        # SCANNER ID
        # -------------------------------------------------

        scanner_ids = _split_multi_values(

            row.get(

                "Scanner ID",

                row.get(

                    "Plugin ID",

                    row.get(
                        "QID",
                        "",
                    ),
                ),
            )
        )

        if not scanner_ids:
            scanner_ids = [""]

        # -------------------------------------------------
        # CVEs
        # -------------------------------------------------

        cves = _split_multi_values(
            row.get(
                "CVE",
                "",
            )
        )

        if not cves:
            # CVE fallback rule: use scanner/plugin identifier when CVE is missing.
            cves = scanner_ids[:] if scanner_ids else [""]

        row_keys = []

        for host in hosts:

            for scanner_id in scanner_ids:

                for cve in cves:

                    # -------------------------------------
                    # SPECIAL:
                    # VAMS CVE contains scanner ID digits
                    # -------------------------------------

                    special_scanner_match = (

                        _is_numeric_like(cve)

                        and

                        cve == scanner_id
                    )

                    # -------------------------------------
                    # TIER 1
                    # -------------------------------------

                    for port in ports:

                        row_keys.append({

                            "tier": 1,

                            "key":
                                f"{host}|"
                                f"{name}|"
                                f"{cve}|"
                                f"{scanner_id}|"
                                f"{port}",

                            "port": port,
                        })

                    # -------------------------------------
                    # TIER 2
                    # Host + Name + CVE + ScannerID
                    # -------------------------------------

                    row_keys.append({

                        "tier": 2,

                        "key":
                            f"{host}|"
                            f"{name}|"
                            f"{cve}|"
                            f"{scanner_id}",

                        "ports": ports,
                    })

                    # -------------------------------------
                    # TIER 3
                    # ONLY IF BOTH HAVE NO CVE
                    # -------------------------------------

                    if not cve:

                        row_keys.append({

                            "tier": 3,

                            "key":
                                f"{host}|"
                                f"{name}|"
                                f"{scanner_id}",
                        })

                    # -------------------------------------
                    # SPECIAL TIER 3A
                    # CVE contains scanner digits
                    # -------------------------------------

                    if special_scanner_match:

                        row_keys.append({

                            "tier": 3,

                            "key":
                                f"{host}|"
                                f"{name}|"
                                f"{scanner_id}",
                        })

            # -------------------------------------------------
            # TIER 4
            # -------------------------------------------------

            row_keys.append({

                "tier": 4,

                "key":
                    f"{host}|"
                    f"{name}",
            })

        all_rows.append(row_keys)

    return all_rows

# ---------------------------------------------------------
# FAST LOOKUP ENGINE
# ---------------------------------------------------------

class FastVamsEnrichmentEngine:

    def __init__(self):
        self.lookup = {}
        self.lookup_multi = {}

    def build_vams_lookup(
        self,
        vams_df: pd.DataFrame,
    ):
    
        """
        Builds fast lookup table
        using enterprise tiered keys.
        """
    
        keys_list = build_fast_keys(
            vams_df
        )
    
        for idx, keys in enumerate(
            keys_list
        ):
    
            row = (
                vams_df.iloc[idx]
                .to_dict()
            )
    
            for meta in keys:
            
                key = meta["key"]
    
                # ---------------------------------------------
                # Preserve FIRST occurrence
                # ---------------------------------------------
    
                if key not in self.lookup:
                    self.lookup[key] = row

                self.lookup_multi.setdefault(key, []).append(row)

    def enrich(
        self,
        target_df: pd.DataFrame,
    ) -> pd.DataFrame:
    
        out = target_df.copy()
    
        keys_list = build_fast_keys(out)
    
        for idx, row_keys in enumerate(keys_list):
            matched_row = None
            matched_meta = None
            matched_rows = []

            # -------------------------------------------------
            # TIERED SEARCH
            # -------------------------------------------------
            for meta in row_keys:
                current_rows = self.lookup_multi.get(meta["key"], [])
                if current_rows:
                    matched_meta = meta
                    matched_rows = current_rows
                    matched_row = current_rows[0]
                    break

            if matched_row is None:
                continue
            
            # -------------------------------------------------
            # STRICT TIER 3 VALIDATION
            # BOTH SIDES MUST HAVE NO CVE
            # -------------------------------------------------
    
            if matched_meta["tier"] == 3:
            
                current_cve = str(
                
                    out.at[
                        idx,
                        "CVE",
                    ]
    
                ).strip()
    
                matched_cve = str(
                
                    matched_row.get(
                        "CVE",
                        "",
                    )
    
                ).strip()
    
                if (
                
                    current_cve
                    and current_cve.lower()
                    not in [
                        "nan",
                        "none",
                    ]
    
                ) or (
                
                    matched_cve
                    and matched_cve.lower()
                    not in [
                        "nan",
                        "none",
                    ]
    
                ):
    
                    continue
                
            # -------------------------------------------------
            # PORT MERGING
            # -------------------------------------------------
    
            if matched_meta["tier"] == 2:
            
                existing_port = str(
                
                    out.at[
                        idx,
                        "Port",
                    ]
    
                ).strip()
    
                incoming_port = str(
                
                    matched_row.get(
                        "Port",
                        "",
                    )
    
                ).strip()
    
                merged_ports = []
    
                for p in [
                
                    existing_port,
                    incoming_port,
                ]:
    
                    if not p:
                        continue
                    
                    for split_p in re.split(
                        r"[;,]",
                        p,
                    ):
    
                        split_p = split_p.strip()
    
                        if (
                            split_p
                            and split_p
                            not in merged_ports
                        ):
    
                            merged_ports.append(
                                split_p
                            )
    
                out.at[
                    idx,
                    "Port",
                ] = merge_semicolon(merged_ports)
    
            # -------------------------------------------------
            # WRITE VAMS COLUMNS
            # -------------------------------------------------
    
            source_rows = matched_rows or [matched_row]

            for col in VAMS_COLUMNS:
                if col not in out.columns:
                    out[col] = ""

                existing_val = str(
                    out.at[
                        idx,
                        col,
                    ]
                ).strip()

                incoming_values = []
                for source_row in source_rows:
                    incoming_val = str(
                        source_row.get(
                            col,
                            "",
                        )
                    ).strip()
                    if (
                        incoming_val
                        and incoming_val.lower() not in ["nan", "none"]
                        and incoming_val not in incoming_values
                    ):
                        incoming_values.append(incoming_val)

                if not incoming_values:
                    continue

                # ---------------------------------------------
                # FILL ONLY LOGIC (NO OVERWRITE)
                # ---------------------------------------------
                if _is_empty(existing_val):
                    out.at[
                        idx,
                        col,
                    ] = merge_semicolon(incoming_values)
    
        return out
