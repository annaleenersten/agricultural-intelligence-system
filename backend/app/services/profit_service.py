from backend.app.services.price_service import get_crop_price
from ml.data.locationsAndCrops_config import COST_PER_ACRE


def calculate_profit(crop, predicted_yield):

    crop = crop.upper()

    price_df = get_crop_price(crop)


    if price_df is None or price_df.empty:
        return None


    # Get newest available price
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