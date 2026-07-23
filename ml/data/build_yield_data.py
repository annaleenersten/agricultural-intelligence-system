# year
# state
# county
# crop
# yield
# previous_year_yield
# five_year_avg_yield
# yield_change

import pandas as pd
import os

from backend.app.services.crop_service import get_crop_yield_data
from ml.data.locationsAndCrops_config import STATES, CROPS


OUTPUT_FILE = "ml/data/processed/yield_data.csv"

START_YEAR = "2010"


def add_yield_history(df):

    df = df.sort_values(
        ["state", "county", "crop", "year"]
    )


    df["previous_year_yield"] = (
        df.groupby(
            ["state","county","crop"]
        )["yield"]
        .shift(1)
    )


    df["five_year_avg_yield"] = (
        df.groupby(
            ["state","county","crop"]
        )["yield"]
        .transform(
            lambda x:
            x.shift(1)
             .rolling(5)
             .mean()
        )
    )


    df["yield_change"] = (
        df["yield"] -
        df["previous_year_yield"]
    )


    return df



def build_yield_data():

    rows = []


    for crop in CROPS:

        for state in STATES:

            print(
                f"Fetching {crop} - {state}"
            )


            try:

                df = get_crop_yield_data(
                    crop,
                    state,
                    START_YEAR
                )


                if df.empty:
                    continue


                rows.append(df)


            except Exception as e:

                print(
                    f"Error {crop}-{state}: {e}"
                )


    if not rows:

        print("No yield data")
        return



    df = pd.concat(
        rows,
        ignore_index=True
    )


    df["state"] = (
        df["state"]
        .str.upper()
        .str.strip()
    )


    df["county"] = (
        df["county"]
        .str.replace(
            " COUNTY",
            "",
            regex=False
        )
        .str.upper()
        .str.strip()
    )


    df["crop"] = (
        df["crop"]
        .str.upper()
        .str.strip()
    )


    df = add_yield_history(df)


    os.makedirs(
        "ml/data/processed",
        exist_ok=True
    )


    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    print(
        "Saved:",
        len(df),
        "rows"
    )


if __name__ == "__main__":
    build_yield_data()