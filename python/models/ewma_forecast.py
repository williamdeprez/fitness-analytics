import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    # Load processed data
    processed_path = Path(__file__).resolve().parents[2] / "data" / "processed"
    df = pd.read_csv(processed_path / "training_lift_day_aggregates.csv")

    df["date"] = pd.to_datetime(df["date"])

    # Filter bench press data
    bench = (
        df[df["exercise"].str.contains("bench press", na=False)]
        .sort_values("date")
        .copy()
    )

    if bench.empty:
        raise ValueError("No bench press data found.")

    # Generate forecasts
    horizon = 21

    maintain = forecast_fatigue_scenario(bench, horizon=horizon, mode="maintain")
    reduce = forecast_fatigue_scenario(bench, horizon=horizon, mode="reduce")
    deload = forecast_fatigue_scenario(bench, horizon=horizon, mode="deload")

    # Prepare time axis
    last_date = bench["date"].iloc[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=horizon,
        freq="D"
    )

    history_window_days = 90

    cutoff_date = last_date - pd.Timedelta(days=history_window_days)

    bench_recent = bench[bench["date"] >= cutoff_date].copy()

    # Plot
    plt.figure(figsize=(12, 6))

    # Historical EWMA
    plt.plot(
        bench_recent["date"],
        bench_recent["ewma_stress"],
        label="Observed",
        linewidth=1.8,
        alpha=0.7,
        color="steelblue"
    )

    # Vertical divider
    plt.axvline(last_date, linestyle="--", color="black", alpha=0.6)

    # Forecast region shading
    xmin = float(mdates.date2num(last_date))
    xmax = float(mdates.date2num(future_dates[-1]))

    plt.axvspan(
        xmin,
        xmax,
        color="gray",
        alpha=0.08
    )

    # Forecast curves
    plt.plot(future_dates, maintain["forecasted_ewma"],
             label="Maintain", linestyle="--", linewidth=2, color="orange")

    plt.plot(future_dates, reduce["forecasted_ewma"],
             label="Reduce 30%", linestyle="--", linewidth=2, color="green")

    plt.plot(future_dates, deload["forecasted_ewma"],
             label="Deload", linestyle="-", linewidth=2.5, color="red")

    plt.title("EWMA Fatigue Forecasting Scenarios – Bench Press")
    plt.xlabel("Date")
    plt.ylabel("EWMA Fatigue")
    plt.ylim(bottom=0)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --------------------------------------------------
    # 6. Print combined forecast
    # --------------------------------------------------
    combined = pd.concat([maintain, reduce, deload], ignore_index=True)
    print(combined)
