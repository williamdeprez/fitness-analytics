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

def add_fatigue_phase(df: pd.DataFrame, ewma_span: int = 14, slope_smooth_span: int = 7, tol: float = 5) -> pd.DataFrame:
    """
    Classifies fatigue phase based on EWMA slope of EWMA stress.
    
    :param df: The DataFrame produced from add_rolling_load()
    :type df: pd.DataFrame
    :param ewma_span: Span for EWMA smoothing of stress levels
    :param slope_smooth_span: Span for EWMA smoothing of slope
    :param tol: Tolerance for classifying stable phase
    :return: Returns the original DataFrame with an additional column classifying fatigue phase.
    :rtype: DataFrame
    """
    df = df.copy()
    df = df.sort_values(["exercise", "date"])

    def classify_fatigue_phase(slope):
        if slope > tol:
            return "accumulating"
        elif slope < -tol:
            return "recovering"
        else:
            return "stable"

    df["ewma_smooth"] = (
        df
        .groupby("exercise")["ewma_stress"]
        .transform(lambda x: x.ewm(span=ewma_span, adjust=False).mean())
    )

    df["ewma_slope"] = df.groupby("exercise")["ewma_smooth"].diff()

    df["ewma_slope_smooth"] = (
        df
        .groupby("exercise")["ewma_slope"]
        .transform(lambda x: x.ewm(span=slope_smooth_span, adjust=False).mean())
    )

    df["fatigue_phase"] = df["ewma_slope_smooth"].apply(classify_fatigue_phase)

    return df

def aggregate_fatigue_phases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate consecutive fatigue phases into duration-based summaries.

    :param df: DataFrame with `fatigue_phase`, `ewma_stress`, and `stress`.
    :return: DataFrame summarizing fatigue phases.
    """
    df = df.copy()
    df = df.sort_values(["exercise", "date"])

    # Identify phase transitions
    df["phase_group"] = (
        df.groupby("exercise")["fatigue_phase"]
          .transform(lambda x: (x != x.shift()).cumsum())
    )

    # Aggregate phase metrics
    phase_summary = (
        df.groupby(["exercise", "phase_group", "fatigue_phase"], as_index=False)
          .agg(
              start_date=("date", "min"),
              end_date=("date", "max"),
              calendar_days=("date", lambda x: (x.max() - x.min()).days + 1),
              mean_ewma=("ewma_stress", "mean"),
              mean_stress=("stress", "mean"),
              sessions = ("date", "count")
          )
    )
    return phase_summary

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
        "ewma_stress": "mean",
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