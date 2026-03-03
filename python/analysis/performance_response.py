import numpy as np
import pandas as pd

def performance_response_curve(
    model,
    base_row: pd.Series,
    fatigue_feature: str = "ewma_stress",
    fatigue_min: float | None = None,
    fatigue_max: float | None = None,
    n_points: int = 100,
) -> pd.DataFrame:

    if fatigue_feature not in base_row.index:
        raise ValueError(f"{fatigue_feature} not in base_row")

    base_value = float(base_row[fatigue_feature])

    if fatigue_min is None:
        fatigue_min = float(0.5 * base_value)

    if fatigue_max is None:
        fatigue_max = float(1.5 * base_value)

    fatigue_range = np.linspace(
        float(fatigue_min),
        float(fatigue_max),
        int(n_points)
    )

    rows = []

    for val in fatigue_range:
        row = base_row.copy()
        row[fatigue_feature] = val
        rows.append(row)

    X = pd.DataFrame(rows)

    predictions = model.predict(X)

    return pd.DataFrame({
        fatigue_feature: fatigue_range,
        "predicted_performance": predictions
    })

if __name__ == "__main__":
    from pathlib import Path
    import pandas as pd
    from python.models.regression import (
        train_ridge_regression,
        encode_fatigue_phase,
    )

    processed_path = Path(__file__).resolve().parents[2] / "data" / "processed"
    df = pd.read_csv(processed_path / "model_bench_regression.csv")

    target = "max_weight"

    features = [
        "ewma_stress",
        "days_since_last_session",
        "fatigue_phase"
    ]

    alpha = 1000  # use your tuned value here if different

    model, feature_columns = train_ridge_regression(
        data=df,
        target=target,
        features=features,
        alpha=alpha,
        phase_baseline="accumulating"
    )

    df_model = df[features + [target]].dropna().copy()

    X = encode_fatigue_phase(
        df_model[features],
        baseline="accumulating"
    )

    X = X[feature_columns]

    base_row = X.iloc[-1]

    response_df = performance_response_curve(
        model=model,
        base_row=base_row,
        fatigue_feature="ewma_stress"
    )

    print("\nPerformance Response Curve Preview:")
    print(response_df.head())
    print(response_df.tail())