from load_data import load_training_data
import pandas as pd
from pathlib import Path
from feature_engineering import aggregate_lift_day

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

def write_output(df: pd.DataFrame, filename: str) -> None:
    out_path = PROCESSED_DIR / filename
    df.to_csv(out_path, index=False)

    print(f"Saved normalized data to {out_path}")
    

def main():
    PROCESSED_DIR.mkdir(exist_ok=True)

    df = load_training_data()

    write_output(df, "training_sets_normalized.csv")
    write_output(aggregate_lift_day(df), "training_lift_day_aggregates.csv")


if __name__ == "__main__":
    main()