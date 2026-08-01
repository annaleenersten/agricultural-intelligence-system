import requests
import pandas as pd


API_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

API_KEY = "1039D34B-EA23-3138-ABC0-5A0CA8E069EC"


# USDA reporting units for each crop
PRICE_UNITS = {
    "CORN": "$ / BU",
    "SOYBEANS": "$ / BU",
    "WHEAT": "$ / BU",
    "BARLEY": "$ / BU",
    "OATS": "$ / BU",
    "RICE": "$ / CWT",
    "COTTON": "CENTS / LB"
}


def get_crop_price(crop, start_year="2010"):

    crop = crop.upper()

    unit = PRICE_UNITS.get(crop)

    if unit is None:
        print(f"Unsupported crop: {crop}")
        return pd.DataFrame()

    params = {
        "key": API_KEY,
        "commodity_desc": crop,
        "statisticcat_desc": "PRICE RECEIVED",
        "unit_desc": unit,
        "year__GE": start_year,
        "format": "JSON"
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        print(f"[PRICE ERROR] {crop}: {e}")
        return pd.DataFrame()

    if "data" not in data or not data["data"]:

        print(f"[PRICE EMPTY] {crop}")
        return pd.DataFrame()

    df = pd.DataFrame(data["data"])

    # Required columns
    required = [
        "year",
        "commodity_desc",
        "Value"
    ]

    for col in required:
        if col not in df.columns:
            df[col] = None

    # Clean price column
    df["Value"] = (
        df["Value"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
    )

    df["Value"] = pd.to_numeric(
        df["Value"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["year", "Value"]
    )

    if df.empty:
        return pd.DataFrame()

    df = df.rename(
        columns={
            "commodity_desc": "crop",
            "Value": "price"
        }
    )

    df["crop"] = df["crop"].str.upper()

    df["year"] = df["year"].astype(int)

    df = (
        df.groupby(
            ["crop", "year"],
            as_index=False
        )["price"]
        .mean()
    )

    return df
