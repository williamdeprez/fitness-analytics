import pandas as pd

def report_missingness(df, name="DataFrame"):
    missing = df.isna().mean().sort_values(ascending=False)
    print(f"\nMissingness report for {name}:")
    print((missing * 100).round(2))

if __name__ == "__main__":
    df = pd.read_csv("data/processed/training_lift_day_aggregates.csv")
    report_missingness(df, "Lift-Day Aggregates")
