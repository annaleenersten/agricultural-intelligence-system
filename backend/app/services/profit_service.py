import pandas as pd
from ml.data.locationsAndCrops_config import COST_PER_ACRE

PRICE_DF = pd.read_csv("ml/data/price_data.csv")

def get_latest_price(crop):
    crop = crop.upper()

    prices = PRICE_DF[
        PRICE_DF["crop"].str.upper() == crop
    ]

    if prices.empty:
        return None

    latest_row = prices.sort_values("year").iloc[-1]

    return {
    "year": int(latest_row["year"]),
    "price": float(latest_row["price"])
}


def calculate_profit(crop, predicted_yield):
    crop = crop.upper()

    price_info = get_latest_price(crop)
    cost = COST_PER_ACRE.get(crop)

    if price_info is None or cost is None:
        return None

    price = price_info["price"]

    revenue = predicted_yield * price
    profit = revenue - cost

    return {
        "price_year": price_info["year"],
        "price_per_bushel": price,
        "cost_per_acre": cost,
        "revenue_per_acre": revenue,
        "profit_per_acre": profit,
    }