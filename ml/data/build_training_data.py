from backend.app.services.crop_service import get_crop_yield_data
from backend.app.services.weather_service import get_weather_features
import pandas as pd


def build_training_data():

    usda = get_crop_yield_data("CORN", "WA", "2015")

    if usda is None or "error" in usda:
        print("USDA failed")
        return

    for _, row in usda.iterrows():

        year = row["year"]

        weather = get_weather_features(
            48.42,
            -122.33,
            f"{year}-01-01",
            f"{year}-12-31"
        )

    weather_df = pd.DataFrame([weather] * len(usda))

    df = pd.concat([usda.reset_index(drop=True), weather_df], axis=1)

    df = df.dropna()

    df.to_csv("ml/data/training_data.csv", index=False)

    print(df.head())
    print("Saved training data")

    return df


if __name__ == "__main__":
    build_training_data()