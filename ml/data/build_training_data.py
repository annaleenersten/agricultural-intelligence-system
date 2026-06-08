import pandas as pd
import joblib
import os

from backend.app.services.crop_service import get_crop_yield_data
from ml.data.locationsAndCrops_config import STATES, CROPS

# -----------------------------
# CONFIG
# -----------------------------
START_YEAR = 2018
END_YEAR = 2023

OUTPUT_FILE = "ml/data/training_data.csv"
FEATURE_FILE = "ml/models/features.pkl"


# -----------------------------
# LOAD USDA DATA SAFELY
# -----------------------------
def load_usda_data(crop, state):
    try:
        df = get_crop_yield_data(crop, state, str(START_YEAR))

        if df is None or isinstance(df, dict):
            return None

        return df

    except Exception as e:
        print(f"[USDA ERROR] {state}-{crop}: {e}")
        return None


# -----------------------------
# BUILD DATASET (BASELINE ONLY)
# -----------------------------
def build_training_data():

    rows = []

    print("\nBuilding baseline training dataset (NO WEATHER)\n")

    for crop in CROPS:
        for state in STATES:

            print(f"Processing {crop} - {state}")

            df = load_usda_data(crop, state)

            if df is None or df.empty:
                print(f"Skipping {state}-{crop}")
                continue

            for _, r in df.iterrows():

                try:
                    year = int(r["year"])
                    yield_value = pd.to_numeric(r["yield"], errors="coerce")

                    if year < START_YEAR or year > END_YEAR:
                        continue

                    if pd.isna(yield_value):
                        continue

                    rows.append({
                        "year": year,
                        "state": state.upper(),
                        "county": str(r.get("county", "STATE_LEVEL")).upper(),
                        "crop": crop.upper(),
                        "yield": float(yield_value),
                    })

                except Exception as e:
                    print("Row error:", e)
                    continue

    # -----------------------------
    # DATAFRAME
    # -----------------------------
    df = pd.DataFrame(rows)

    if df.empty:
        print("❌ No data generated")
        return None

    # clean
    df = df.dropna()

    # -----------------------------
    # ONE-HOT ENCODING
    # -----------------------------
    df = pd.get_dummies(df, columns=["state", "county", "crop"])

    # -----------------------------
    # FEATURES
    # -----------------------------
    feature_cols = [c for c in df.columns if c != "yield"]

    joblib.dump(feature_cols, FEATURE_FILE)

    # -----------------------------
    # SAVE CSV
    # -----------------------------
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n✅ DONE")
    print(f"Rows: {len(df)}")
    print(f"Features: {len(feature_cols)}")

    return df


if __name__ == "__main__":
    build_training_data()