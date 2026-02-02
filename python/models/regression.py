import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score

def encode_fatigue_phase(X: pd.DataFrame, baseline: str) -> pd.DataFrame:
    phases = ["accumulating", "recovering", "stable"]

    if baseline not in phases:
        raise ValueError(f"Baseline must be one of {phases}")

    ordered = [baseline] + [p for p in phases if p != baseline]

    X = X.copy()
    X["fatigue_phase"] = pd.Categorical(
        X["fatigue_phase"],
        categories=ordered,
        ordered=False
    )

    return pd.get_dummies(
        X,
        columns=["fatigue_phase"],
        drop_first=True
    )

def print_model_information(model, X_train: pd.DataFrame, X_test: pd.DataFrame, y_test: pd.Series, model_name: str = "Model") -> None:
    """
    Prints evaluation metrics and coefficients for a trained regression model.

    :param model: Trained sklearn regression model
    :param X_train: Training feature matrix
    :param X_test: Test feature matrix
    :param y_train: Training target
    :param y_test: Test target
    :param model_name: Display name for the model
    """

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n{model_name} Performance")
    print(f"  MSE: {mse:.2f}")
    print(f"  R^2: {r2:.3f}")
    print(f"  Training rows: {len(X_train)}")
    print(f"  Test rows: {len(X_test)}")

    # Coefficient inspection (if supported)
    if hasattr(model, "coef_"):
        coef_table = pd.DataFrame({
            "feature": X_train.columns,
            "coefficient": model.coef_
        }).sort_values("coefficient", key=abs, ascending=False)

        print("\nModel coefficients:")
        print(coef_table)

        coef_table.to_csv(
            f"data/processed/{model_name.lower().replace(' ', '_')}_coefficients.csv",
            index=False
        )

def train_regression_model(data: pd.DataFrame, target: str, features: list, phase_baseline: str = "accumulating") -> LinearRegression:
    # Select features + target
    df = data[features + [target]].copy()

    # Drop rows with missing values
    df = df.dropna()

    X = df[features]
    y = df[target]

    # One-hot encode fatigue_phase
    X = encode_fatigue_phase(X, baseline=phase_baseline)

    print("Rows before dropna:", len(data))
    print("Rows after dropna:", len(df))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    print_model_information(
        model,
        X_train,
        X_test,
        y_test,
        model_name="Linear Regression"
    )

    return model

def train_ridge_regression(data: pd.DataFrame, target: str, features: list, alpha: float = 1.0, phase_baseline: str = "accumulating") -> Ridge:
    # Select features + target
    df = data[features + [target]].copy()

    # Drop rows with missing values
    df = df.dropna()

    X = df[features]
    y = df[target]

    # One-hot encode fatigue_phase
    X = encode_fatigue_phase(X, baseline=phase_baseline)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)

    print_model_information(
        model,
        X_train,
        X_test,
        y_test,
        model_name="Ridge Regression"
    )

    return model