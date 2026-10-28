from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_YIELD_FILE = ROOT / "ml" / "data" / "raw" / "qs.crops_20261028.txt"
RAW_COST_FILE = ROOT / "ml" / "data" / "raw" / "cop_forecast.csv"


def _normalize_crop(value):
    if value is None:
        return ""
    return str(value).upper().strip()


def _normalize_county(value):
    if value is None:
        return ""
    return str(value).upper().replace(" COUNTY", "").strip()


def _empty_yield_frame():
    return pd.DataFrame(columns=["state", "county", "crop", "year", "yield"])


def load_raw_yield_enrichment():
    if not RAW_YIELD_FILE.exists():
        return _empty_yield_frame()

    chunks = []
    try:
        reader = pd.read_csv(
            RAW_YIELD_FILE,
            sep="\t",
            encoding="latin1",
            on_bad_lines="skip",
            dtype=str,
            chunksize=50000,
            keep_default_na=False,
        )
        for chunk in reader:
            chunk = chunk.copy()
            chunk = chunk[
                chunk["STATISTICCAT_DESC"].fillna("").str.upper().eq("YIELD")
            ]
            chunk = chunk[
                chunk["AGG_LEVEL_DESC"].fillna("").str.upper().eq("COUNTY")
            ]
            chunk = chunk[
                chunk["UNIT_DESC"].fillna("").str.upper().str.contains("BU / ACRE")
            ]

            if chunk.empty:
                continue

            chunk["year"] = pd.to_numeric(chunk["YEAR"], errors="coerce")
            chunk["yield"] = pd.to_numeric(
                chunk["VALUE"].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )
            chunk = chunk[chunk["year"].notna() & chunk["yield"].notna()]
            if chunk.empty:
                continue

            chunk["state"] = chunk["STATE_ALPHA"].astype(str).str.upper().str.strip()
            chunk["county"] = chunk["COUNTY_NAME"].map(_normalize_county)
            chunk["crop"] = chunk["COMMODITY_DESC"].map(_normalize_crop)
            chunks.append(
                chunk[["state", "county", "crop", "year", "yield"]].drop_duplicates()
            )
    except OSError:
        return _empty_yield_frame()

    if not chunks:
        return _empty_yield_frame()

    return pd.concat(chunks, ignore_index=True).drop_duplicates()


def load_raw_cost_projection():
    if not RAW_COST_FILE.exists():
        return pd.DataFrame(columns=["crop", "year", "cost_per_acre"])

    cost_df = pd.read_csv(RAW_COST_FILE, dtype=str)
    cost_df = cost_df[
        cost_df["Category"].fillna("").str.strip().str.casefold().eq("operating costs")
    ]
    cost_df = cost_df[
        cost_df["Item"].fillna("").str.strip().str.casefold().eq("total, operating costs")
    ]
    cost_df = cost_df.dropna(subset=["Commodity", "Year", "Value"])
    cost_df = cost_df.copy()
    cost_df["crop"] = cost_df["Commodity"].map(_normalize_crop)
    cost_df["year"] = pd.to_numeric(
        cost_df["Year"].astype(str).str.replace("F", "", regex=False),
        errors="coerce",
    )
    cost_df["cost_per_acre"] = pd.to_numeric(cost_df["Value"], errors="coerce")
    cost_df = cost_df[
        cost_df["crop"].ne("")
        & cost_df["year"].notna()
        & cost_df["cost_per_acre"].notna()
    ]
    return cost_df[["crop", "year", "cost_per_acre"]].drop_duplicates()


if __name__ == "__main__":
    yield_rows = load_raw_yield_enrichment()
    print(f"Raw yield enrichment rows: {len(yield_rows)}")
    cost_rows = load_raw_cost_projection()
    print(f"Raw cost rows: {len(cost_rows)}")
