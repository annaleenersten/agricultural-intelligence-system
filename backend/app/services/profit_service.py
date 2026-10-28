import pandas as pd

from ml.data.locationsAndCrops_config import COST_PER_ACRE


PRICE_FILE = "ml/data/processed/price_data.csv"


def calculate_profit(crop, predicted_yield):

    crop = crop.upper()

    price_df = pd.read_csv(PRICE_FILE)
    price_df["crop"] = price_df["crop"].astype(str).str.upper().str.strip()
    price_df["year"] = pd.to_numeric(price_df["year"], errors="coerce")
    price_df["price"] = pd.to_numeric(price_df["price"], errors="coerce")
    price_df = price_df[
        (price_df["crop"] == crop)
        & price_df["year"].notna()
        & price_df["price"].notna()
    ]

    if price_df.empty:
        return None


    price_row = (
        price_df
        .sort_values("year")
        .iloc[-1]
    )


    price = float(
        price_row["price"]
    )


    year = int(
        price_row["year"]
    )


    cost = COST_PER_ACRE.get(crop)


    if cost is None:
        return None


    revenue = (
        float(predicted_yield)
        *
        price
    )


    profit = (
        revenue
        -
        float(cost)
    )


    return {

        "crop": crop,

        "price_year": year,

        "price_per_unit": price,

        "cost_per_acre": float(cost),

        "revenue_per_acre": revenue,

        "profit_per_acre": profit
    }