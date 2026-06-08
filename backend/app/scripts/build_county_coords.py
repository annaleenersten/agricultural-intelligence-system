import pandas as pd
import joblib

df = pd.read_csv(
    "backend/app/data/2025_Gaz_counties_national.txt",
    sep="|"
)

df.columns = df.columns.str.strip()

df = df[["USPS", "NAME", "INTPTLAT", "INTPTLONG"]]

df.columns = ["state", "county", "lat", "lon"]

df["county"] = df["county"].str.replace(" County", "", regex=False).str.upper()

county_coords = {}

for _, row in df.iterrows():
    key = (row["state"], row["county"])
    county_coords[key] = (float(row["lat"]), float(row["lon"]))

joblib.dump(county_coords, "ml/models/county_coords.pkl")

print("Saved county coordinates!")