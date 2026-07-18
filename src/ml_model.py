"""
ml_model.py
Automatic ML task detection, model training, and evaluation.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score, confusion_matrix
)


def detect_task_type(df: pd.DataFrame, target_column: str) -> str:
    """Return 'classification' or 'regression' based on the target column's nature."""
    series = df[target_column].dropna()
    if pd.api.types.is_numeric_dtype(series):
        unique_ratio = series.nunique() / len(series) if len(series) else 0
        if series.nunique() <= 15 and unique_ratio < 0.05:
            return "classification"
        return "regression"
    return "classification"


def get_usable_features(df: pd.DataFrame, target_column: str) -> list:
    """Return columns usable as ML features (exclude target, IDs, and free text/high-cardinality)."""
    features = []
    n_rows = len(df)
    for col in df.columns:
        if col == target_column:
            continue
        if df[col].nunique() > 0.9 * n_rows and df[col].dtype == object:
            continue  # likely an ID or free-text column
        features.append(col)
    return features


def prepare_data(df: pd.DataFrame, target_column: str, feature_columns: list):
    """Encode categorical features/target, impute missing values, scale numeric features."""
    data = df[feature_columns + [target_column]].copy()
    data = data.dropna(subset=[target_column])

    for col in feature_columns:
        if pd.api.types.is_datetime64_any_dtype(data[col]):
            # Convert datetime features into a numeric ordinal (unix seconds)
            data[col] = data[col].astype("int64") // 10**9
            data[col] = data[col].fillna(data[col].median())
        elif pd.api.types.is_numeric_dtype(data[col]):
            data[col] = data[col].fillna(data[col].median())
        else:
            data[col] = data[col].fillna("Unknown")
            data[col] = LabelEncoder().fit_transform(data[col].astype(str))

    task_type = detect_task_type(df, target_column)
    target_encoder = None
    if task_type == "classification" and not pd.api.types.is_numeric_dtype(data[target_column]):
        target_encoder = LabelEncoder()
        data[target_column] = target_encoder.fit_transform(data[target_column].astype(str))

    X = data[feature_columns]
    y = data[target_column]

    return X, y, task_type, target_encoder


def train_model(X, y, task_type: str, algorithm: str, test_size: float = 0.2):
    """
    algorithm options:
      classification: 'random_forest', 'logistic_regression'
      regression: 'linear_regression', 'random_forest'
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42,
        stratify=y if task_type == "classification" and y.nunique() > 1 else None
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    if task_type == "classification":
        if algorithm == "logistic_regression":
            model = LogisticRegression(max_iter=1000)
        else:
            model = RandomForestClassifier(n_estimators=200, random_state=42)
    else:
        if algorithm == "linear_regression":
            model = LinearRegression()
        else:
            model = RandomForestRegressor(n_estimators=200, random_state=42)

    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    metrics = {}
    if task_type == "classification":
        avg = "binary" if y.nunique() == 2 else "weighted"
        metrics["accuracy"] = round(accuracy_score(y_test, y_pred), 4)
        metrics["precision"] = round(precision_score(y_test, y_pred, average=avg, zero_division=0), 4)
        metrics["recall"] = round(recall_score(y_test, y_pred, average=avg, zero_division=0), 4)
        metrics["f1_score"] = round(f1_score(y_test, y_pred, average=avg, zero_division=0), 4)
        metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
    else:
        metrics["rmse"] = round(np.sqrt(mean_squared_error(y_test, y_pred)), 4)
        metrics["mae"] = round(mean_absolute_error(y_test, y_pred), 4)
        metrics["r2_score"] = round(r2_score(y_test, y_pred), 4)

    feature_importance = None
    if hasattr(model, "feature_importances_"):
        feature_importance = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    elif hasattr(model, "coef_"):
        coef = model.coef_
        coef = coef[0] if coef.ndim > 1 else coef
        feature_importance = pd.Series(np.abs(coef), index=X.columns).sort_values(ascending=False)

    return {
        "model": model,
        "scaler": scaler,
        "metrics": metrics,
        "y_test": y_test,
        "y_pred": y_pred,
        "feature_importance": feature_importance,
        "task_type": task_type,
    }
