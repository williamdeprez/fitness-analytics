from load_data import load_training_data
import pandas as pd
from pathlib import Path
from feature_engineering import (
    aggregate_lift_day,
    add_stress_metrics,
    add_rolling_load,
    add_time_since_last_session,
    aggregate_global_daily_fatigue,
    add_fatigue_phase
)

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

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
    write_output(lift_day, "training_lift_day_aggregates.csv")

    daily = aggregate_global_daily_fatigue(lift_day)
    write_output(daily, "training_global_daily_fatigue.csv")

    print(lift_day.describe())
    print(daily.describe())

if __name__ == "__main__":
    main()