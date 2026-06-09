# year,state,county,crop,yield

import pandas as pd
import os

from backend.app.services.crop_service import get_crop_yield_data
from ml.data.locationsAndCrops_config import STATES, CROPS

OUTPUT_FILE = "ml/data/yield_data.csv"

START_YEAR = 2020


def build_yield_data():

    rows = []

    for crop in CROPS:
        for state in STATES:

            print(f"Processing {crop} - {state}")

            try:
                df = get_crop_yield_data(
                    crop,
                    state,
                    str(START_YEAR)
                )

                if df is None or isinstance(df, dict):
                    continue

                rows.append(df)

            except Exception as e:
                print(e)

    if not rows:
        print("No yield data generated")
        return

    df = pd.concat(rows, ignore_index=True)

    df = df.dropna(subset=["yield"])

    os.makedirs("ml/data", exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Yield dataset saved")
    print("Rows:", len(df))


if __name__ == "__main__":
    build_yield_data()