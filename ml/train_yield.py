import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# 1. LOAD TRAINING DATA
df = pd.read_csv("ml/data/training_data.csv")

# 2. SPLIT FEATURES (X) AND TARGET (y)
X = df[["avg_temp", "total_rain", "avg_wind"]]
y = df["yield"]

# 3. TRAIN MODEL
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# 4. SAVE MODEL
joblib.dump(model, "ml/models/yield_model.pkl")

print("Model trained and saved!")