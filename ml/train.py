import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor


TRAINING_FILE = "ml/data/processed/training_data.csv"
MODEL_FILE = "ml/models/crop_model.pkl"
FEATURE_FILE = "ml/models/features.pkl"


# -----------------------------
# LOAD DATA
# -----------------------------

df = pd.read_csv(TRAINING_FILE)

print("Training rows:", len(df))


# -----------------------------
# TARGET
# -----------------------------

y = df["yield"]


# -----------------------------
# FEATURES
# -----------------------------

X = df.drop(
    columns=[
        "yield",
        "yield_change"
    ]
)


categorical = [
    "state",
    "county",
    "crop"
]


X = pd.get_dummies(
    X,
    columns=categorical
)


# -----------------------------
# TRAIN
# -----------------------------

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)


# -----------------------------
# SAVE
# -----------------------------

os.makedirs(
    "ml/models",
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_FILE
)

joblib.dump(
    X.columns.tolist(),
    FEATURE_FILE
)

print()

print("Model trained!")

print("Features:", len(X.columns))
