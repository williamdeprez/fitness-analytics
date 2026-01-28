# This file defines the v1 feature schema. Changes should be intentional and model-driven.
import pandas as pd
import numpy as np

def aggregate_lift_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts raw, set-level data into one row per exercise per day.
    
    :param df: The raw DataFrame loaded from load_training_data()
    :type df: pd.DataFrame
    :return: Returns data grouped and sorted appropriately with sums for volume, weight maxes, total reps, mean rpe
    :rtype: DataFrame
    """
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
    """
    Transforms raw workload into physiologically meaningful training stress.
    
    :param df: the DataFrame produced from aggregate_lift_day()
    :type df: pd.DataFrame
    :return: Returns the original DataFrame with stress metrics
    :rtype: DataFrame
    """
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
    """
    Adds memory to training stress using rolling windows and EWMA.
    
    :param df: the DataFrame produced from aggregate_lift_day()
    :type df: pd.DataFrame
    :param windows: Stress windows tuple, default=(7,14)
    :param ewma_span: How quickly should past training stress fade in importance
    :return: Returns the original DataFrame with rolling load metrics
    :rtype: DataFrame
    """
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

def add_time_since_last_session(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a column for the length of time in days since the last time that exercise was performed.
    
    :param df: The DataFrame produced from add_rolling_load()
    :type df: pd.DataFrame
    :return: Returns the original DataFrame with an additional column calculating the number of days since the last exercise.
    :rtype: DataFrame
    """
    df = df.copy()
    df = df.sort_values(["exercise", "date"])

    df["days_since_last_session"] = (
        df
        .groupby("exercise")["date"]
        .diff()
        .map(lambda x: x.days if pd.notna(x) else np.nan)
    )

    return df

def aggregate_global_daily_fatigue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates lift-level stress into systemic, whole-body daily fatigue.
    
    :param df: The DataFrame produced from the pipeline of the other functions within feature_engineering.py
    :type df: pd.DataFrame
    :return: Computes a systematic view of stress and fatigue and returns a DataFrame containing that information.
    :rtype: DataFrame
    """
    rolling_cols = [c for c in df.columns if c.startswith("rolling_stress_")]

    agg_dict = {
        "stress": "sum",
        "ewma_stress": "sum",
        "exercise": "nunique",
    }

    for col in rolling_cols:
        agg_dict[col] = "sum"
        
    daily = (
        df
        .groupby("date", as_index=False)
        .agg(agg_dict)
        .rename(columns={
            "stress": "total_stress",
            "exercise": "num_lifts",
        })
    )

    return daily