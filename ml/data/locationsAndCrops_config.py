import joblib

STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
  "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
  "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
  "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

COUNTY_COORDS = joblib.load("ml/models/county_coords.pkl")

CROPS = ["CORN", "WHEAT", "SOYBEANS"]

COST_PER_ACRE = {
    "CORN": 800,
    "SOYBEANS": 450,
    "WHEAT": 350,
}

