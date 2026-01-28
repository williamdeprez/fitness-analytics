import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

def load_training_data(filename: str = "strong_workouts.csv") -> pd.DataFrame:
    """
    Ingests the raw DataFrame exported from Strong exercise tracking app, and sorts it into appropriate columns.
    
    :param filename: The filename of the csv to ingest, under the path "data/raw/---.csv"
    :type filename: str
    :return: Returns a DataFrame containing Date, Workout Name, Exercise Name, Sets, Weight, Reps, and RPE
    :rtype: DataFrame
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    df = df.rename(columns={
        "Date": "datetime",
        "Workout Name": "workout",
        "Exercise Name": "exercise",
        "Set Order": "set",
        "Weight": "weight",
        "Reps": "reps",
        "RPE": "rpe",
    })

    required_cols = {
        "datetime", "workout", "exercise", "set", "weight", "reps", "rpe"
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns after rename: {missing}")

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["date"] = pd.to_datetime(df["datetime"].values.astype("datetime64[D]"))

    df["exercise"] = (df["exercise"].str.lower().str.strip())

    df["workout"] = (df["workout"].fillna("unknown").str.lower().str.strip())

    numeric_cols = ["weight", "reps", "rpe", "set"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Drop cardio, etc
    df = df[(df["reps"] > 0) & (df["weight"] > 0)]

    df["volume"] = df["weight"] * df["reps"]

    df = df[
        [
            "date",
            "datetime",
            "workout",
            "exercise",
            "set",
            "weight",
            "reps",
            "rpe",
            "volume"
        ]
    ]

    df = df.sort_values(["datetime", "exercise", "set"]).reset_index(drop=True)
    
    return df
