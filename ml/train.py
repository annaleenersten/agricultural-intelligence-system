# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# import joblib


# yield_df = pd.read_csv("ml/data/yield_data.csv")
# weather_df = pd.read_csv("ml/data/weather_data.csv")

# training_df = yield_df.merge(
#     weather_df,
#     on=["state", "county", "year"],
#     how="inner"
# )

# print(training_df.head())
# print(training_df.columns.tolist())

# X = training_df.drop(columns=["yield"])
# y = training_df["yield"]

# model = RandomForestRegressor(n_estimators=200, random_state=42)
# model.fit(X, y)

# joblib.dump(model, "ml/models/crop_model.pkl")

# print("Model trained")

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os


YIELD_PATH = "ml/data/yield_data.csv"
WEATHER_PATH = "ml/data/weather_data.csv"
MODEL_PATH = "ml/models/crop_model.pkl"


# -----------------------------
# CLEANING
# -----------------------------
def clean_yield(df):
    df = df.copy()

    df["state"] = df["state"].astype(str).str.upper().str.strip()
    df["county"] = df["county"].astype(str).str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # remove bad rows (THIS FIXES YOUR NaNs)
    df = df.dropna(subset=["county", "year"])

    return df


def clean_weather(df):
    df = df.copy()

    df["state"] = df["state"].astype(str).str.upper().str.strip()
    df["county"] = df["county"].astype(str).str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df = df.dropna(subset=["county", "year"])

    return df


# -----------------------------
# LOAD DATA
# -----------------------------
yield_df = pd.read_csv(YIELD_PATH)
weather_df = pd.read_csv(WEATHER_PATH)

yield_df = clean_yield(yield_df)
weather_df = clean_weather(weather_df)

print("Yield rows:", len(yield_df))
print("Weather rows:", len(weather_df))


# -----------------------------
# DEBUG OVERLAP (IMPORTANT)
# -----------------------------
yield_keys = set(zip(yield_df.state, yield_df.county, yield_df.year))
weather_keys = set(zip(weather_df.state, weather_df.county, weather_df.year))

print("Yield keys:", len(yield_keys))
print("Weather keys:", len(weather_keys))
print("Overlap keys:", len(yield_keys & weather_keys))


# -----------------------------
# MERGE
# -----------------------------
training_df = yield_df.merge(
    weather_df,
    on=["state", "county", "year"],
    how="inner"
)

print("\nTraining rows:", len(training_df))

if len(training_df) == 0:
    raise ValueError("No training data after merge — check county/state/year alignment")


# -----------------------------
# FEATURES / TARGET
# -----------------------------
X = training_df.drop(columns=["yield"])
y = training_df["yield"]

# FORCE all categorical columns into numeric
categorical_cols = ["state", "county", "crop"]

X = pd.get_dummies(X, columns=categorical_cols)

# safety: ensure no strings remain
print("\nFeature dtypes check:")
print(X.dtypes[X.dtypes == "object"])

if len(X.select_dtypes(include=["object"]).columns) > 0:
    raise ValueError("Still have string columns in X — encoding failed")

# -----------------------------
# MODEL
# -----------------------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

# -----------------------------
# SAVE
# -----------------------------
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)

print("\nModel trained successfully")
print("Final feature count:", X.shape[1])

