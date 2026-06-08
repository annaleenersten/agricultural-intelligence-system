import requests
import pandas as pd
import time

API_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
API_KEY = "1039D34B-EA23-3138-ABC0-5A0CA8E069EC"


# ----------------------------
# CLEAN RAW USDA DATA
# ----------------------------
def clean_usda_data(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    # remove forecast rows
    if "reference_period_desc" in df.columns:
        df = df[~df["reference_period_desc"].str.contains("FORECAST", na=False)]

    # keep only yield data
    df = df[df.get("statisticcat_desc", "") == "YIELD"]

    # numeric conversion
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    # drop bad rows
    df = df.dropna(subset=["Value", "year"])

    return df


# ----------------------------
# MAIN API FUNCTION
# ----------------------------
def get_crop_yield_data(crop="CORN", state="WA", start_year="2015"):

    params = {
        "key": API_KEY,
        "commodity_desc": crop,
        "statisticcat_desc": "YIELD",
        "unit_desc": "BU / ACRE",
        "domain_desc": "TOTAL",
        "state_alpha": state,
        "year__GE": start_year,
        "format": "JSON"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print(f"[USDA ERROR] {state}-{crop}: {e}")
        return pd.DataFrame()

    # ----------------------------
    # VALIDATE RESPONSE
    # ----------------------------
    if "data" not in data or not data["data"]:
        print(f"[USDA EMPTY] {state}-{crop}")
        return pd.DataFrame()

    df = pd.DataFrame(data["data"])

    # ----------------------------
    # REQUIRED COLUMNS SAFETY CHECK
    # ----------------------------
    required_cols = [
        "year",
        "state_alpha",
        "county_name",
        "commodity_desc",
        "Value"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # ----------------------------
    # CLEAN
    # ----------------------------
    df = clean_usda_data(df)

    if df.empty:
        return pd.DataFrame()

    # ----------------------------
    # STANDARDIZE OUTPUT FORMAT
    # ----------------------------
    df = df.rename(columns={
        "state_alpha": "state",
        "county_name": "county",
        "commodity_desc": "crop",
        "Value": "yield"
    })

    df = df[["year", "state", "county", "crop", "yield"]]

    df["year"] = df["year"].astype(int)
    df["yield"] = pd.to_numeric(df["yield"], errors="coerce")

    return df