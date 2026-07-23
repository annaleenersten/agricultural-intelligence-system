from backend.app.services.price_service import get_crop_price
from ml.data.locationsAndCrops_config import COST_PER_ACRE


def calculate_profit(crop, predicted_yield):

    crop = crop.upper()

    price_info = get_crop_price(crop)

    cost = COST_PER_ACRE.get(crop)


    if price_info is None:
        return None

    if cost is None:
        return None


    price = price_info["price"]


    revenue = predicted_yield * price


    profit = revenue - cost


    return {

        "crop": crop,

        "price_year": price_info["year"],

        "price_per_unit": price,

        "cost_per_acre": cost,

        "revenue_per_acre": revenue,

        "profit_per_acre": profit
    }