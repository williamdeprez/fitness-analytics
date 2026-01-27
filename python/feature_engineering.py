import pandas as pd
import numpy as np

def aggregate_lift_day(df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        df.groupby(["date", "exercise"], as_index=False)
        .agg(
            total_volume=("volume", "sum"),
            max_weight=("weight", "max"),
            total_sets=("set", "count"),
            total_reps=("reps", "sum"),
            mean_rpe=("rpe", "mean"),
            rpe_coverage=("rpe", lambda x: x.notna().mean()),
        )
    )
    return agg

def add_stress_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["stress_volume"] = df["total_volume"]
    df["stress_rpe"] = df["total_volume"] * df["mean_rpe"]

    df["stress"] = np.where(
        df["rpe_coverage"] > 0,
        df["stress_rpe"],
        df["stress_volume"]
    )

    return df

def add_rolling_load(df: pd.DataFrame, windows=(7, 14), ewma_span=7) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["exercise", "date"])

    for w in windows:
        df[f"rolling_stress_{w}d"] = (
            df
            .groupby("exercise")["stress"]
            .transform(lambda x: x.rolling(w, min_periods=1).sum())
        )

    df["ewma_stress"] = (
        df
        .groupby("exercise")["stress"]
        .transform(lambda x: x.ewm(span=ewma_span, adjust=False).mean())
    )

    return df