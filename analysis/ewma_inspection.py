import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

def classify_fatigue_phase(slope, tol=5):
    if slope > tol:
        return "accumulating"
    elif slope < -tol:
        return "recovering"
    else:
        return "stable"

def main():
    phase_colors = {
        "accumulating": "red",
        "stable": "gray",
        "recovering": "green",
    }

    legend_elements = [
        Line2D([0], [0], color="red", lw=2, label="Accumulating"),
        Line2D([0], [0], color="gray", lw=2, label="Stable"),
        Line2D([0], [0], color="green", lw=2, label="Recovering"),
    ]
    
    
    df = pd.read_csv("data/processed/training_lift_day_aggregates.csv")
    df["date"] = pd.to_datetime(df["date"])

    bench = df[df["exercise"].str.contains("bench press", na=False)].sort_values("date").sort_values("date")

    bench["ewma_smooth"] = (
        bench["ewma_stress"]
        .ewm(span=14, adjust=False)
        .mean()
    )

    bench["ewma_slope"] = bench["ewma_smooth"].diff()

    bench["ewma_slope_smooth"] = (
        bench["ewma_slope"]
        .ewm(span=7, adjust=False)
        .mean()
    )

    bench["fatigue_phase"] = bench["ewma_slope_smooth"].apply(classify_fatigue_phase)


    fig, ax1 = plt.subplots(figsize=(12,6))

    # EWMA level
    for i in range(1, len(bench)):
        phase = bench.iloc[i]["fatigue_phase"]
        color = phase_colors[phase]

        ax1.plot(
            bench["date"].iloc[i-1:i+1],
            bench["ewma_smooth"].iloc[i-1:i+1],
            color=color,
            linewidth=1.5
        )


    ax1.set_ylabel("Fatigue Level (EWMA)")
    ax1.legend(handles=legend_elements, title="Fatigue Phase", loc="upper left")

    # Secondary axis for slope
    ax2 = ax1.twinx()
    # ax2.plot(
        # bench["date"],
        # bench["ewma_slope_smooth"],
        # label="Smoothed EWMA Slope",
        # color="black",
        # alpha=0.4
    # )
    ax2.axhline(0, linestyle="--", linewidth=1)
    ax2.set_ylabel("Fatigue Trend (Δ)")
    ax2.legend(loc="upper right")

    # Date formatting
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    ax1.set_title("Bench Press Fatigue Level and Trend")
    ax1.set_xlabel("Date")

    plt.tight_layout()
    plt.show()

    # The smoothed EWMA stress signal reveals long-term fatigue trends that align with known training events. 
    # In particular, a pronounced decline corresponds to a documented injury period, while a recent sustained increase reflects intentional load escalation toward a new bench press PR. 
    # This suggests EWMA stress captures meaningful latent fatigue rather than short-term noise.

if __name__ == "__main__":
    main()