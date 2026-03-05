import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

    response_df = pd.DataFrame({
        fatigue_feature: fatigue_range,
        "predicted_performance": predictions
    })

    response_df["is_current"] = np.isclose(
        response_df[fatigue_feature],
        base_value,
        rtol=1e-4
    )

    return response_df

def plot_predictions(response_df: pd.DataFrame, fatigue_feature: str = "ewma_stress") -> None:
    plt.figure(figsize=(10, 6))

    plt.plot(
        response_df[fatigue_feature],
        response_df["predicted_performance"],
        linewidth=2
    )

    current_row = response_df[response_df["is_current"]]

    if not current_row.empty:
        current_fatigue = current_row[fatigue_feature].iloc[0]
        current_perf = current_row["predicted_performance"].iloc[0]

        plt.axvline(
            current_fatigue,
            linestyle="--",
            linewidth=1.5
        )

        plt.scatter(
            current_fatigue,
            current_perf,
            s=60,
            zorder=3
        )

    plt.xlabel("Fatigue Level")
    plt.ylabel("Predicted Performance")
    plt.title("Predicted Performance vs Fatigue")
    plt.tight_layout()
    plt.show()

def simulate_adaptation_gain(ewma_coef: float, current_ewma: float, pct_increase: float) -> dict:
    target_ewma = current_ewma * (1 + pct_increase)
    delta_ewma = target_ewma - current_ewma
    predicted_gain = ewma_coef * delta_ewma

    return {
        "pct_increase": pct_increase,
        "target_ewma": target_ewma,
        "delta_ewma": delta_ewma,
        "predicted_strength_gain": predicted_gain
    }
    

if __name__ == "__main__":
    from pathlib import Path
    import pandas as pd
    from models.regression import (
        train_ridge_regression,
        encode_fatigue_phase,
    )

    processed_path = Path(__file__).resolve().parents[1] / "data" / "processed"
    df = pd.read_csv(processed_path / "model_bench_regression.csv")

    target = "max_weight"

    features = [
        "ewma_stress",
        "days_since_last_session",
        "fatigue_phase"
    ]

    from run_pipeline import RIDGE_ALPHA_V1

    model, feature_columns = train_ridge_regression(
        data=df,
        target=target,
        features=features,
        alpha=RIDGE_ALPHA_V1,
        phase_baseline="accumulating"
    )

    coef_series = pd.Series(
        model.coef_,
        index=feature_columns
    )

    print("\nCoefficient Table:")
    print(coef_series.sort_values())

    mean_ewma = df["ewma_stress"].mean()
    mean_perf = df["max_weight"].mean()

    elasticity = coef_series["ewma_stress"] * mean_ewma / mean_perf

    print("Elasticity:", elasticity)

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

    ewma_coef = coef_series["ewma_stress"]
    current_ewma = base_row["ewma_stress"]

        
    stress_scenarios = [i / 100 for i in range(-10, 21, 5)]

    results = []

    for pct in stress_scenarios:
        result = simulate_adaptation_gain(
            ewma_coef=ewma_coef,
            current_ewma=current_ewma,
            pct_increase=pct
        )
        results.append(result)

    results_df = pd.DataFrame(results)

    print("\nAdaptation Simulation (Chronic Load Increase):")
    print(results_df)

    plot_predictions(response_df)