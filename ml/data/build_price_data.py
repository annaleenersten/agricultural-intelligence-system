import os
import pandas as pd

from backend.app.services.price_service import get_crop_price
from ml.data.locationsAndCrops_config import CROPS


OUTPUT_FILE = "ml/data/processed/price_data.csv"

START_YEAR = "2010"


def build_price_data():

    rows = []

    for crop in CROPS:

        print(f"Fetching prices for {crop}")

        try:

            df = get_crop_price(crop, START_YEAR)

            if df.empty:
                print(f"No price data found for {crop}")
                continue

            rows.append(df)

        except Exception as e:

            print(f"{crop}: {e}")

    if not rows:

        print("No price data generated.")
        return

    price_df = pd.concat(
        rows,
        ignore_index=True
    )

    os.makedirs(
        "ml/data/processed",
        exist_ok=True
    )

    price_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Price dataset saved")
    print(f"Rows: {len(price_df)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_price_data()