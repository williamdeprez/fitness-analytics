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