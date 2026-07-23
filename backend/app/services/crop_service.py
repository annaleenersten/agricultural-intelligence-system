import requests
import pandas as pd


API_URL = (
    "https://quickstats.nass.usda.gov/api/api_GET/"
)

API_KEY = "1039D34B-EA23-3138-ABC0-5A0CA8E069EC"



def get_crop_yield_data(
        crop,
        state,
        start_year="2010"
):


    params = {

        "key": API_KEY,

        "commodity_desc": crop,

        "statisticcat_desc": "YIELD",

        "unit_desc": "BU / ACRE",

        "state_alpha": state,

        "year__GE": start_year,

        "format": "JSON"
    }


    response = requests.get(
        API_URL,
        params=params,
        timeout=30
    )


    response.raise_for_status()


    data = response.json()


    if "data" not in data:
        return pd.DataFrame()


    df = pd.DataFrame(data["data"])


    df = df[
        df["reference_period_desc"]
        .str.contains(
            "FORECAST",
            case=False,
            na=False
        )
        == False
    ]


    df = df[
        df["statisticcat_desc"]
        == "YIELD"
    ]


    df["Value"] = pd.to_numeric(
        df["Value"],
        errors="coerce"
    )


    df = df.dropna(
        subset=["Value"]
    )


    return pd.DataFrame({

        "year":
            df["year"].astype(int),

        "state":
            df["state_alpha"],

        "county":
            df["county_name"],

        "crop":
            df["commodity_desc"],

        "yield":
            df["Value"]

    })