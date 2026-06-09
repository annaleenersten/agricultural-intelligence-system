import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib


yield_df = pd.read_csv("ml/data/yield_data.csv")
weather_df = pd.read_csv("ml/data/weather_data.csv")

training_df = yield_df.merge(
    weather_df,
    on=["state", "county", "year"],
    how="inner"
)

X = training_df.drop(columns=["yield"])
y = training_df["yield"]

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

joblib.dump(model, "ml/models/crop_model.pkl")

print("Model trained")