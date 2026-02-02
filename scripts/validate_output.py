import pandas as pd

# Load data

lift_day = pd.read_csv(
    "data/processed/training_lift_day_aggregates.csv",
    parse_dates=["date"]
)

phase_summary = pd.read_csv(
    "data/processed/fatigue_phase_summary.csv",
    parse_dates=["start_date", "end_date"]
)

# Focus on ONE lift

PATTERN = "bench press"

ld = lift_day[lift_day["exercise"].str.contains(PATTERN, na=False)].copy()
ps = phase_summary[phase_summary["exercise"].str.contains(PATTERN, na=False)].copy()

# Count actual lift sessions per phase

computed_lift_days = []

for row in ps.itertuples():
    count = (
        (ld["date"] >= row.start_date) &
        (ld["date"] <= row.end_date)
    ).sum()

    computed_lift_days.append(int(count))

ps["computed_lift_days"] = computed_lift_days

# Print comparison table

print(
    ps[
        [
            "fatigue_phase",
            "start_date",
            "end_date",
            "calendar_days",
            "computed_lift_days",
        ]
    ]
)

# Verify full coverage (no gaps, no overlaps)

covered_idx = set()

for row in ps.itertuples():
    idx = ld[
        (ld["date"] >= row.start_date) &
        (ld["date"] <= row.end_date)
    ].index

    covered_idx.update(idx)

print("\nCoverage check:")
print("Lift-day rows:", len(ld))
print("Covered rows:", len(covered_idx))
