import requests
import pandas as pd

API_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
API_KEY = "1039D34B-EA23-3138-ABC0-5A0CA8E069EC"


def get_crop_yield_data(crop="CORN", state="WA", start_year="2015"):

    #-----------------------
    # API parameters
    #-----------------------
    params = {
        "key": API_KEY,
        "commodity_desc": crop,
        "statisticcat_desc": "YIELD",
        "state_alpha": state,
        "year__GE": start_year,
        "format": "JSON"
    }

    #-----------------------
    # API request
    #-----------------------
    response = requests.get(API_URL, params=params)
    data = response.json()

    #-----------------------
    # Check for errors
    #-----------------------
    if "data" not in data:
        return {"error": "No data returned", "raw": data}

    #-----------------------------
    # Process data into DataFrame
    #-----------------------------
    records = data["data"]

    df = pd.DataFrame(records)

    df = df[["year", "state_alpha", "commodity_desc", "Value"]]
    df.columns = ["year", "state", "crop", "yield"]

    #--------------------------------------------------
    # Convert yield to numeric, coercing errors to NaN
    #--------------------------------------------------
    df["yield"] = pd.to_numeric(df["yield"], errors="coerce")

    return df