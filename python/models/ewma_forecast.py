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

def summarize_scenarios(scenarios: dict, threshold: float) -> pd.DataFrame:
    rows = []

    for name, forecast_df in scenarios.items():
        days = days_until_recovery(forecast_df, threshold)

        rows.append({
            "scenario": name,
            "days_until_recovery": days,
            "final_fatigue": forecast_df["forecasted_ewma"].iloc[-1],
            "percent_drop": (
                (forecast_df["forecasted_ewma"].iloc[0] -
                 forecast_df["forecasted_ewma"].iloc[-1])
                / forecast_df["forecasted_ewma"].iloc[0]
            ) * 100
        })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    processed_path = Path(__file__).resolve().parents[2] / "data" / "processed"
    df = pd.read_csv(processed_path / "training_lift_day_aggregates.csv")

    df["date"] = pd.to_datetime(df["date"])

    bench = (
        df[df["exercise"].str.contains("bench press", na=False)]
        .sort_values("date")
        .copy()
    )

    if bench.empty:
        raise ValueError("No bench press data found.")

    horizon = 21

    maintain = forecast_fatigue_scenario(bench, horizon=horizon, mode="maintain")
    reduce = forecast_fatigue_scenario(bench, horizon=horizon, mode="reduce")
    deload = forecast_fatigue_scenario(bench, horizon=horizon, mode="deload")

    last_date = bench["date"].iloc[-1]

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=horizon,
        freq="D"
    )

    threshold = bench["ewma_stress"].quantile(0.25)

    scenarios = {
        "maintain": maintain,
        "reduce_30": reduce,
        "deload": deload
    }

    summary = summarize_scenarios(scenarios, threshold)
    print(summary)

    deload_days = summary.loc[
        summary["scenario"] == "deload",
        "days_until_recovery"
    ].iloc[0]

    recovery_date = None
    if pd.notna(deload_days):
        recovery_date = last_date + pd.Timedelta(days=int(deload_days))

    history_window_days = 90
    cutoff_date = last_date - pd.Timedelta(days=history_window_days)
    bench_recent = bench[bench["date"] >= cutoff_date].copy()

    plt.figure(figsize=(12, 6))

    plt.plot(
        bench_recent["date"],
        bench_recent["ewma_stress"],
        label="Observed",
        linewidth=1.8,
        alpha=0.7,
        color="steelblue"
    )

    plt.axvline(last_date, linestyle="--", color="black", alpha=0.6)

    xmin = float(mdates.date2num(last_date))
    xmax = float(mdates.date2num(future_dates[-1]))
    plt.axvspan(xmin, xmax, color="gray", alpha=0.08)

    plt.plot(
        future_dates,
        maintain["forecasted_ewma"],
        label="Maintain",
        linestyle="--",
        linewidth=2,
        color="orange"
    )

    plt.plot(
        future_dates,
        reduce["forecasted_ewma"],
        label="Reduce 30%",
        linestyle="--",
        linewidth=2,
        color="green"
    )

    plt.plot(
        future_dates,
        deload["forecasted_ewma"],
        label="Deload",
        linestyle="-",
        linewidth=2.5,
        color="red"
    )

    if recovery_date is not None:
        plt.axvline(
            recovery_date,
            color="red",
            linestyle=":",
            linewidth=2,
            alpha=0.8,
            label="Deload Recovery Date"
        )

        plt.axhline(
            threshold,
            color="gray",
            linestyle="--",
            alpha=0.5
        )

    plt.title("EWMA Fatigue Forecasting Scenarios – Bench Press")
    plt.xlabel("Date")
    plt.ylabel("EWMA Fatigue")
    plt.ylim(bottom=0)
    plt.legend()
    plt.tight_layout()
<<<<<<< HEAD
    plt.show()
=======
    plt.show()

    combined = pd.concat([maintain, reduce, deload], ignore_index=True)
    print(combined)

    maintain_days = days_until_recovery(maintain, threshold)
    reduce_days = days_until_recovery(reduce, threshold)
    deload_days = days_until_recovery(deload, threshold)

    print(f"Maintain recovery days: {maintain_days}")
    print(f"Reduce recovery days: {reduce_days}")
    print(f"Deload recovery days: {deload_days}")
>>>>>>> 22a09edc0890c83c9aa77a457bc832b582f9dd62
