import pandas as pd

df = pd.read_csv("data/processed/training_lift_day_aggregates.csv")

features = [
    "ewma_stress",
    "days_since_last_session",
    "ewma_slope_magnitude",
    "max_weight"
]

corr = df[features].corr()
print(corr)
