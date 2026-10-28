from datetime import datetime

import pandas as pd

from backend.app.services.price_service import PRICE_UNITS, get_crop_price
from ml.data.locationsAndCrops_config import COST_PER_ACRE
from ml.data.raw_data_enrichment import load_raw_cost_projection


PRICE_FILE = "ml/data/processed/price_data.csv"


def calculate_profit(crop, predicted_yield, state=None):

    crop = crop.upper()

    price_df = get_crop_price(crop, state=state) if state else pd.DataFrame()
    price_source = (
        f"USDA {state.upper()} state average"
        if state
        else "USDA processed crop average (location unavailable)"
    )

    if price_df.empty:
        price_df = pd.read_csv(PRICE_FILE)
        price_df["crop"] = price_df["crop"].astype(str).str.upper().str.strip()
        price_df["year"] = pd.to_numeric(price_df["year"], errors="coerce")
        price_df["price"] = pd.to_numeric(price_df["price"], errors="coerce")
        price_df = price_df[
            (price_df["crop"] == crop)
            & price_df["year"].notna()
            & price_df["price"].notna()
        ]
        price_source = "USDA processed crop average (location unavailable)"

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

    cost_year = datetime.now().year
    cost_rows = load_raw_cost_projection()
    cost_rows = cost_rows[cost_rows["crop"] == crop]

    if not cost_rows.empty:
        cost_rows = cost_rows.assign(
            year_difference=(cost_rows["year"] - cost_year).abs()
        ).sort_values(["year_difference", "year"])
        cost_row = cost_rows.iloc[0]
        cost = float(cost_row["cost_per_acre"])
        cost_year = int(cost_row["year"])
        cost_source = f"USDA U.S. projected operating costs ({cost_year})"
    else:
        cost = COST_PER_ACRE.get(crop)
        cost_source = "App estimate (not location-specific)"

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

        "price_unit": PRICE_UNITS.get(crop, "per unit"),

        "price_source": price_source,

        "cost_per_acre": float(cost),

        "cost_year": cost_year,

        "cost_source": cost_source,

        "revenue_per_acre": revenue,

        "profit_per_acre": profit
    }