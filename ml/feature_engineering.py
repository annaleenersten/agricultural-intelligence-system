def build_features(weather, crop, state):
    return [
        crop,
        state,
        weather["avg_temp"],
        weather["total_rain"],
        weather["avg_wind"]
    ]