import joblib
import pandas as pd

model = joblib.load("ml/models/yield_model.pkl")

sample = pd.DataFrame([{
    "avg_temp": 15.4,
    "total_rain": 1732,
    "avg_wind": 10.6
}])

print(model.predict(sample))