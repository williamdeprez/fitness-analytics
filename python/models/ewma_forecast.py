import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

def forecast_ewma(last_ewma: float, future_stress: np.ndarray, alpha: float) -> np.ndarray:
    ewma_forecast = []
    prev = last_ewma

    for stress in future_stress:
        next_ewma = alpha * stress + (1 - alpha) * prev
        ewma_forecast.append(next_ewma)
        prev = next_ewma

    return np.array(ewma_forecast)


def make_stress_scenario(recent_stress: pd.Series, horizon: int, mode: str = "maintain", scale: float = 0.7) -> np.ndarray:
    mean_stress = recent_stress.mean()

    if mode == "maintain":
        return np.full(horizon, mean_stress)

    if mode == "reduce":
        return np.full(horizon, mean_stress * scale)

    if mode == "deload":
        return np.zeros(horizon)

    raise ValueError(f"Unknown scenario mode: {mode}")

def forecast_fatigue_scenario(df: pd.DataFrame, stress_col: str = "stress", ewma_col: str = "ewma_stress", ewma_span: int = 7, horizon: int = 14, mode: str = "maintain", scale: float = 0.7) -> pd.DataFrame:
    alpha = 2 / (ewma_span + 1)

    recent_stress = df[stress_col].tail(7)
    last_ewma = df[ewma_col].iloc[-1]

    future_stress = make_stress_scenario(
        recent_stress,
        horizon=horizon,
        mode=mode,
        scale=scale
    )

    ewma_forecast = forecast_ewma(
        last_ewma=last_ewma,
        future_stress=future_stress,
        alpha=alpha
    )

    return pd.DataFrame({
        "day_ahead": np.arange(1, horizon + 1),
        "assumed_stress": future_stress,
        "forecasted_ewma": ewma_forecast,
        "scenario": mode
    })

def days_until_recovery(forecast_df: pd.DataFrame, threshold: float) -> Optional[int]:
    below = forecast_df["forecasted_ewma"] < threshold

    if not below.any():
        return None

    return forecast_df.loc[below, "day_ahead"].iloc[0]

if __name__ == "__main__":
    """
    Simple demo run for deterministic fatigue forecasting.
    This does NOT modify the pipeline.
    """

    processed_path = Path(__file__).resolve().parents[2] / "data" / "processed"
    df = pd.read_csv(processed_path / "training_lift_day_aggregates.csv")

    bench = df[df["exercise"].str.contains("bench press", na=False)].copy()

    forecast = forecast_fatigue_scenario(
        bench,
        horizon=21,
        mode="deload"
    )

    threshold = bench["ewma_stress"].quantile(0.25)

    days = days_until_recovery(forecast, threshold)

    print(f"Days until low fatigue state: {days}")

    print(forecast)

    # maintain = forecast_fatigue_scenario(bench, horizon=21, mode="maintain")
    # reduce = forecast_fatigue_scenario(bench, horizon=21, mode="reduce")
    # deload = forecast_fatigue_scenario(bench, horizon=21, mode="deload")

    # combined = pd.concat([maintain, reduce, deload])
    # print(combined)