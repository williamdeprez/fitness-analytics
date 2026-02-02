import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from python.models.regression import tune_ridge_alpha

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

def main():
    lift_day = pd.read_csv(
        DATA_DIR / "training_lift_day_aggregates.csv",
        parse_dates=["date"]
    )

    bench_data = lift_day[
        lift_day["exercise"].str.contains("bench press", na=False)
    ].copy()

    results = tune_ridge_alpha(
        data=bench_data,
        target="max_weight",
        features=[
            "ewma_stress",
            "fatigue_phase",
            "days_since_last_session",
            "sessions_in_phase",
            "ewma_slope_magnitude"
        ],
        alphas=[10**i for i in range(-5, 6)],
        phase_baseline="stable"
    )

    results.to_csv(
        DATA_DIR / "ridge_alpha_tuning_results.csv",
        index=False
    )

if __name__ == "__main__":
    main()
