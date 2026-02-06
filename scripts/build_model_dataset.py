import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

def build_bench_regression_dataset():
    df = pd.read_csv(
        DATA_DIR / "training_lift_day_aggregates.csv",
        parse_dates=["date"]
    )

    bench = df[
        df["exercise"].str.contains("bench press", na=False)
    ].copy()

    features = [
        "date",
        "ewma_stress",
        "days_since_last_session",
        "fatigue_phase",
        "ewma_slope_magnitude",
        "sessions_in_phase",
        "max_weight"
    ]

    bench = bench[features].dropna()

    out_path = DATA_DIR / "model_bench_regression.csv"
    bench.to_csv(out_path, index=False)

    print("Model dataset built:")
    print(f"  Path: {out_path}")
    print(f"  Rows: {len(bench)}")
    print(f"  Columns: {list(bench.columns)}")


if __name__ == "__main__":
    build_bench_regression_dataset()
