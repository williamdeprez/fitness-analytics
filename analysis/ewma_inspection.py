import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv("data/processed/training_lift_day_aggregates.csv")
df["date"] = pd.to_datetime(df["date"])

bench = df[df["exercise"].str.contains("bench press", na=False)].sort_values("date").sort_values("date")

bench["ewma_smooth"] = (
    bench["ewma_stress"]
    .ewm(span=14, adjust=False)
    .mean()
)

fig, ax = plt.subplots(figsize=(12,6))

# ax.plot(bench["date"], bench["stress"], label="Daily Stress", alpha=0.4)
# ax.plot(bench["date"], bench["rolling_stress_7d"], label="7-Day Rolling Stress")
ax.plot(bench["date"], bench["ewma_stress"], label="EWMA Stress", alpha=0.5)
ax.plot(bench["date"], bench["ewma_smooth"], label="Smoothed EWMA", linewidth=2)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.xticks(rotation=45)

ax.set_title("Bench Press Training Stress Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Stress")
ax.legend()

plt.tight_layout()
plt.show()

# The smoothed EWMA stress signal reveals long-term fatigue trends that align with known training events. 
# In particular, a pronounced decline corresponds to a documented injury period, while a recent sustained increase reflects intentional load escalation toward a new bench press PR. 
# This suggests EWMA stress captures meaningful latent fatigue rather than short-term noise.