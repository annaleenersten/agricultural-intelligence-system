import requests


API_URL = (
    "https://quickstats.nass.usda.gov/api/api_GET/"
)

API_KEY = "1039D34B-EA23-3138-ABC0-5A0CA8E069EC"


def get_crop_price(crop, year=None):

    params = {

        "key": API_KEY,

        "commodity_desc": crop,

        "statisticcat_desc":
            "PRICE RECEIVED",

        "unit_desc":
            "$ / BU",

        "format":
            "JSON"
    }


    if year:
        params["year"] = year


    response = requests.get(
        API_URL,
        params=params
    )


    response.raise_for_status()


    data = response.json()


    if "data" not in data:
        return None


    return data["data"]