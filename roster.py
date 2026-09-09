"""
Soldier roster loading. The roster is a simple table (Excel or CSV) with
columns: full_name, personal_number, rank. Column headers are matched
loosely (Hebrew or English, several common spellings) so an existing unit
Excel sheet can usually be used as-is.
"""
import os
import pandas as pd

import config

_NAME_COLS = ["full_name", "name", "שם", "שם מלא", "שם ומשפחה"]
_PN_COLS = ["personal_number", "personal number", "מספר אישי", "מ.א.", "מא"]
_RANK_COLS = ["rank", "דרגה"]


def _find_column(columns, candidates):
    lowered = {str(c).strip().lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    return None


def _normalize(df):
    name_col = _find_column(df.columns, _NAME_COLS)
    pn_col = _find_column(df.columns, _PN_COLS)
    rank_col = _find_column(df.columns, _RANK_COLS)
    if not (name_col and pn_col and rank_col):
        raise ValueError(
            "roster is missing one of the required columns: "
            "full_name / personal_number / rank (Hebrew headers also accepted)"
        )
    out = df[[name_col, pn_col, rank_col]].copy()
    out.columns = ["full_name", "personal_number", "rank"]
    # Drop blank rows (common in hand-maintained sheets) before any string
    # coercion - astype(str) on a NaN cell doesn't reliably yield "nan".
    out = out.dropna(subset=["full_name"])
    out = out[out["full_name"].astype(str).str.strip() != ""]
    out["full_name"] = out["full_name"].astype(str).str.strip()
    out["personal_number"] = (
        out["personal_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    out["rank"] = out["rank"].astype(str).str.strip()
    return out.reset_index(drop=True)


def load_roster():
    """Load the roster from data/roster.xlsx if present, else data/roster.csv."""
    if os.path.exists(config.ROSTER_XLSX):
        df = pd.read_excel(config.ROSTER_XLSX, dtype=str)
    elif os.path.exists(config.ROSTER_CSV):
        df = pd.read_csv(config.ROSTER_CSV, dtype=str)
    else:
        return pd.DataFrame(columns=["full_name", "personal_number", "rank"])
    return _normalize(df)


def find_soldier(full_name):
    """Look up a soldier by exact full-name match. Returns a dict or None."""
    df = load_roster()
    if df.empty:
        return None
    match = df[df["full_name"] == full_name.strip()]
    if match.empty:
        return None
    row = match.iloc[0]
    return {
        "full_name": row["full_name"],
        "personal_number": row["personal_number"],
        "rank": row["rank"],
    }


def all_names():
    df = load_roster()
    return sorted(df["full_name"].tolist()) if not df.empty else []
