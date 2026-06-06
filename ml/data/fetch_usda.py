from backend.app.services.crop_service import get_crop_yield_data
import pandas as pd

if __name__ == "__main__":
    df = get_crop_yield_data("CORN", "WA", "2015")

    if df is None or "error" in df:
        print("No data returned")
    else:
        print(df.head())

        df.to_csv("ml/data/usda_yield.csv", index=False)
        print("Saved to ml/data/usda_yield.csv")