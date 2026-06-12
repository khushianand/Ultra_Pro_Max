from __future__ import annotations

import re
import pandas as pd

THREE_UK_PROJECT = "3uk"

QUALYS_SCANNER = "qualys"


# =========================================================
# TOTAL VULNERABILITIES COLUMNS
# =========================================================

THREE_UK_QUALYS_TOTAL_COLUMNS = [

    "IP",
    "Network",
    "DNS",
    "NetBIOS",
    "Tracking Method",
    "OS",
    "IP Status",
    "QID",
    "Title",
    "Vuln Status",
    "Type",
    "Severity",
    "Port",
    "Protocol",
    "FQDN",
    "SSL",
    "First Detected",
    "Last Detected",
    "Times Detected",
    "Date Last Fixed",
    "CVE ID",
    "Vendor Reference",
    "Bugtraq ID",
    "CVSS",
    "Criticality",
    "CVSS Base",
    "CVSS Temporal",
    "Product",
    "CVSS Environment",
    "CVSS3",
    "CVSS3 Base",
    "CVSS3 Temporal",
    "Threat",
    "Impact",
    "Solution",
    "Exploitability",
    "Associated Malware",
    "Results",
    "PCI Vuln",
    "Ticket State",
    "Instance",
    "Category",
]


# =========================================================
# UNIQUE VULNERABILITIES COLUMNS
# =========================================================

THREE_UK_QUALYS_UNIQUE_COLUMNS = [

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

    # VAMS ENRICHMENT

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


# =========================================================
# REQUIRED RAW QUALYS HEADERS
# =========================================================

VAMS_FIELD_COLUMNS = [

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


QUALYS_REQUIRED_HEADERS = [

    "IP",
    "Network",
    "DNS",
    "NetBIOS",
    "Tracking Method",
    "OS",
    "IP Status",
    "QID",
    "Title",
    "Vuln Status",
    "Type",
    "Severity",
    "Port",
    "Protocol",
    "FQDN",
    "SSL",
    "First Detected",
    "Last Detected",
    "Times Detected",
    "Date Last Fixed",
    "CVE ID",
    "Vendor Reference",
    "Bugtraq ID",
    "CVSS",
    "CVSS Base",
    "CVSS Temporal",
    "CVSS Environment",
    "CVSS3.1",
    "CVSS3.1 Base",
    "CVSS3.1 Temporal",
    "Threat",
    "Impact",
    "Solution",
    "Exploitability",
    "Associated Malware",
    "Results",
    "PCI Vuln",
    "Ticket State",
    "Instance",
    "Category",
]

def is_three_uk_qualys_project(
    project: str,
    scanner: str,
) -> bool:

    return (

        str(project)
        .strip()
        .casefold()
        == THREE_UK_PROJECT

        and

        str(scanner)
        .strip()
        .casefold()
        == QUALYS_SCANNER
    )


def detect_qualys_header_row(
    path: str,
    sheet_name: str,
) -> int:

    preview = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=None,
        nrows=15,
    )

    required_headers = {

        h.strip().lower()

        for h in QUALYS_REQUIRED_HEADERS
    }

    best_row = 0
    best_score = 0

    for idx, row in preview.iterrows():

        headers = {

            str(v)
            .strip()
            .lower()

            for v in row.tolist()

            if pd.notna(v)
        }

        score = len(
            required_headers.intersection(
                headers
            )
        )

        if score > best_score:

            best_score = score
            best_row = idx

    return best_row

def severity_to_criticality(
    value: object,
) -> str:

    if pd.isna(value):
        return ""

    text = str(value).strip()

    if not text:
        return ""

    match = re.search(
        r"\d+(?:\.\d+)?",
        text,
    )

    if not match:
        return ""

    try:

        severity = float(
            match.group(0)
        )

    except ValueError:

        return ""

    if severity <= 4.0:
        return "LOW"

    if severity <= 6.0:
        return "MEDIUM"

    if severity <= 8.0:
        return "HIGH"

    return "CRITICAL"


def criticality_series(
    df: pd.DataFrame,
) -> pd.Series:

    if "Severity" not in df.columns:

        return pd.Series(
            [""] * len(df),
            index=df.index,
            dtype="object",
        )

    severity_series = (

        df["Severity"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return severity_series.apply(
        severity_to_criticality
    )


def map_risk(value):

    mapping = {

        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
    }

    return mapping.get(
        str(value).strip().lower(),
        "Unknown",
    )

def three_uk_qualys_total_view(
    df: pd.DataFrame,
) -> pd.DataFrame:

    out = df.copy()

    # =====================================================
    # CRITICALITY
    # =====================================================

    out["Criticality"] = (
        criticality_series(out)
    )

    # =====================================================
    # OPTIONAL PRODUCT
    # =====================================================

    if "Product" not in out.columns:

        out["Product"] = ""

    # =====================================================
    # CVSS3.1 -> REQUIRED FORMAT
    # =====================================================

    rename_map = {

        "CVSS3.1": "CVSS3",
        "CVSS3.1 Base": "CVSS3 Base",
        "CVSS3.1 Temporal": "CVSS3 Temporal",
    }

    out = out.rename(
        columns=rename_map
    )

    # =====================================================
    # ENSURE REQUIRED COLUMNS
    # =====================================================

    for col in THREE_UK_QUALYS_TOTAL_COLUMNS:

        if col not in out.columns:

            out[col] = ""

    # =====================================================
    # FINAL ORDER
    # Parsed 3UK + Qualys raw data stays in Qualys total-column
    # layout for comparison and mapping. Generate Tracking output
    # sheets map this data into template columns before writing.
    # =====================================================

    out = out[
        THREE_UK_QUALYS_TOTAL_COLUMNS
    ]

    return out.reset_index(
        drop=True
    )

def build_3uk_qualys_total_sheet_df(
    path: str,
    sheet_name: str,
) -> pd.DataFrame:

    header_row = detect_qualys_header_row(
        path,
        sheet_name,
    )

    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=header_row,
    ).fillna("")

    df.columns = (

        df.columns
        .astype(str)
        .str.strip()
    )

    return three_uk_qualys_total_view(
        df
    )

def build_3uk_vams_matching_df(
    total_df: pd.DataFrame,
) -> pd.DataFrame:

    """
    Convert Qualys Total Vulnerabilities
    dataframe into generic matching schema
    required by VAMS enrichment engine.
    """

    out = pd.DataFrame()

    out["Name"] = (
        total_df.get("Title", "")
    )

    out["Host / Image"] = (
        total_df.get("IP", "")
    )

    out["Port"] = (
        total_df.get("Port", "")
    )

    out["CVE"] = (
        total_df.get("CVE ID", "")
    )

    out["Scanner ID"] = (
        total_df.get("QID", "")
    )

    return out.fillna("")


def build_3uk_qualys_template_sheet_df(
    total_df: pd.DataFrame,
) -> pd.DataFrame:

    """Map 3UK Qualys Total rows into the universal tracking template columns."""

    column_mapping = {

        "Scanner ID":
            "QID",

        "CVE":
            "CVE ID",

        "CVSS v2.0 Base Score":
            "CVSS Base",

        "Risk":
            "Criticality",

        "Host / Image":
            "IP",

        "Protocol":
            "Protocol",

        "Port":
            "Port",

        "Name":
            "Title",

        "Synopsis":
            "Impact",

        "Description":
            "Impact",

        "Solution":
            "Solution",

        "See Also":
            "Vendor Reference",

        "Plugin Output":
            "Results",

        "CVSS v3.0 Base Score":
            "CVSS3 Base",
    }

    out = pd.DataFrame(
        index=total_df.index
    )

    for target_col, source_col in (
        column_mapping.items()
    ):

        if source_col not in total_df.columns:

            out[target_col] = ""

            continue

        out[target_col] = (

            total_df[source_col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # =====================================================
    # PRESERVE VAMS COLUMNS WHEN PRESENT
    # =====================================================

    for col in VAMS_FIELD_COLUMNS:

        if col in total_df.columns:

            out[col] = (

                total_df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # =====================================================
    # ENSURE ALL UNIVERSAL TEMPLATE COLUMNS
    # =====================================================

    for col in (
        THREE_UK_QUALYS_UNIQUE_COLUMNS
    ):

        if col not in out.columns:

            out[col] = ""

    out = out[
        THREE_UK_QUALYS_UNIQUE_COLUMNS
    ].fillna("")

    return out.astype(str).reset_index(
        drop=True
    )


def build_3uk_qualys_unique_sheet_df(
    total_df: pd.DataFrame,
) -> pd.DataFrame:

    out = build_3uk_qualys_template_sheet_df(
        total_df
    )

    priority = {
        
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    # =====================================================
    # COMMA MERGE
    # =====================================================

    def merge_comma_separated(
        series
    ):

        values = []

        for item in series.dropna():

            item = str(item).strip()

            if not item:
                continue

            split_values = [

                v.strip()

                for chunk in item.split(";")
                for v in chunk.split(",")
            ]

            for value in split_values:

                if (
                    value
                    and value not in values
                ):

                    values.append(value)

        return ", ".join(values)

    # =====================================================
    # AGGREGATION
    # =====================================================

    aggregation = {}

    primary_match_columns = {

        "Scanner ID",
        "CVE",
        "Host / Image",
        "Name",
    }

    for col in (
        THREE_UK_QUALYS_UNIQUE_COLUMNS
    ):

        # -------------------------------------------------
        # PRIMARY MATCHING COLUMNS
        # KEEP CLEAN FOR VAMS MATCHING
        # -------------------------------------------------

        if col in primary_match_columns:

            continue

        # -------------------------------------------------
        # RISK PRIORITY
        # -------------------------------------------------

        if col == "Risk":

            aggregation[col] = (
                lambda s: max(
                    (
                        str(v).strip()
                        for v in s
                    ),
                    key=lambda r:
                        priority.get(r, 0),
                    default="Low",
                )
            )

        # -------------------------------------------------
        # ALL OTHER COLUMNS
        # -------------------------------------------------

        else:

            aggregation[col] = (
                merge_comma_separated
            )

    # =====================================================
    # DEDUPLICATION BASIS
    # =====================================================

    group_cols = [

        "Scanner ID",
        "CVE",
        "Host / Image",
        "Name",
    ]

    return (

        out

        .groupby(
            group_cols,
            dropna=False,
            sort=False,
        )

        .agg(aggregation)

        .reset_index()
        .reindex(
            columns=THREE_UK_QUALYS_UNIQUE_COLUMNS
        )
    )