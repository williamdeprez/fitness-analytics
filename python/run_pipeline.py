from load_data import load_training_data
import pandas as pd
from pathlib import Path
from feature_engineering import (
    aggregate_lift_day,
    add_stress_metrics,
    add_rolling_load,
    add_time_since_last_session,
    aggregate_global_daily_fatigue,
    add_fatigue_phase,
    aggregate_fatigue_phases,
    add_phase_dynamics,
    add_phase_transition_flags,
    add_stress_deviation
)
from models.regression import train_regression_model, train_ridge_regression

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
RIDGE_ALPHA_V1 = 1e4 # Pre-determined best alpha from prior tuning using tune_ridge_alpha

def write_output(df: pd.DataFrame, filename: str) -> None:
    """
    Helper function to write output files and print a notification to console.
    
    :param df: The DataFrame we wish to write to a file
    :type df: pd.DataFrame
    :param filename: Filename for output ex:"training_sets_normalized.csv". Writes to path "data/processed/---"
    :type filename: str
    """
    out_path = PROCESSED_DIR / filename
    df.to_csv(out_path, index=False)

    print(f"Saved normalized data to {out_path}")
    

def main():
    PROCESSED_DIR.mkdir(exist_ok=True)

    df = load_training_data()

    write_output(df, "training_sets_normalized.csv")

    lift_day = aggregate_lift_day(df)
    lift_day = add_stress_metrics(lift_day)
    lift_day = add_rolling_load(lift_day)
    lift_day = add_time_since_last_session(lift_day)
    lift_day = add_fatigue_phase(lift_day)
    lift_day = add_phase_dynamics(lift_day)
    lift_day = add_phase_transition_flags(lift_day)
    lift_day = add_stress_deviation(lift_day)
    write_output(lift_day, "training_lift_day_aggregates.csv")

    daily = aggregate_global_daily_fatigue(lift_day)
    write_output(daily, "training_global_daily_fatigue.csv")

    phase_summary = aggregate_fatigue_phases(lift_day)
    write_output(phase_summary, "fatigue_phase_summary.csv")


    bench_data = lift_day[
        lift_day["exercise"].str.contains("bench press", na=False)
    ].copy()

    # model = train_regression_model(
        # data=bench_data,
        # target="max_weight",
        # features=[
            # "ewma_stress",
            # "fatigue_phase",
            # "sessions_in_phase",
            # "fatigue_phase",
            # "days_since_last_session"
        # ],
        # phase_baseline="accumulating"
    # )

    ridge_model = train_ridge_regression(
        data=bench_data,
        target="max_weight",
        features=[
            "ewma_stress",
            "fatigue_phase",
            "sessions_in_phase",
            "fatigue_phase",
            "days_since_last_session"
        ],
        alpha=RIDGE_ALPHA_V1,
        phase_baseline="accumulating"
    )


if __name__ == "__main__":
    main()