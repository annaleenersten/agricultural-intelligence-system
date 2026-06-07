import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

df = pd.read_csv("ml/data/training_data.csv")

X = df.drop(columns=["yield"])
y = df["yield"]

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

joblib.dump(model, "ml/models/yield_model.pkl")

print("Model trained")