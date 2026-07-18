"""
cleaner.py
Automatic and user-guided data cleaning utilities.
"""

import pandas as pd
import numpy as np


def get_quality_report(df: pd.DataFrame) -> dict:
    """Compute a data quality score and diagnostic breakdown."""
    n_rows, n_cols = df.shape
    total_cells = n_rows * n_cols if n_rows * n_cols > 0 else 1

    missing_cells = df.isna().sum().sum()
    duplicate_rows = df.duplicated().sum()

    missing_pct = (missing_cells / total_cells) * 100
    duplicate_pct = (duplicate_rows / n_rows) * 100 if n_rows else 0

    # Simple weighted quality score (0-100)
    score = 100 - (missing_pct * 0.6) - (duplicate_pct * 0.4)
    score = max(0, min(100, round(score, 1)))

    if score >= 90:
        label = "Excellent"
    elif score >= 75:
        label = "Good"
    elif score >= 50:
        label = "Fair"
    else:
        label = "Poor"

    return {
        "score": score,
        "label": label,
        "missing_cells": int(missing_cells),
        "missing_pct": round(missing_pct, 2),
        "duplicate_rows": int(duplicate_rows),
        "duplicate_pct": round(duplicate_pct, 2),
    }


def detect_outliers_iqr(df: pd.DataFrame, column: str) -> pd.Series:
    """Return a boolean mask of outlier rows for a numeric column using IQR method."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (df[column] < lower) | (df[column] > upper)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def handle_missing_values(df: pd.DataFrame, strategy: str, columns: list = None) -> pd.DataFrame:
    """
    strategy: 'drop_rows', 'drop_columns', 'mean', 'median', 'mode', 'zero', 'ffill', 'bfill'
    """
    df = df.copy()
    cols = columns if columns else df.columns.tolist()

    if strategy == "drop_rows":
        return df.dropna(subset=cols).reset_index(drop=True)

    if strategy == "drop_columns":
        return df.drop(columns=[c for c in cols if df[c].isna().any()])

    for col in cols:
        if col not in df.columns:
            continue
        is_numeric = pd.api.types.is_numeric_dtype(df[col])

        if strategy == "mean" and is_numeric:
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median" and is_numeric:
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "mode":
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val[0])
        elif strategy == "zero":
            df[col] = df[col].fillna(0 if is_numeric else "Unknown")
        elif strategy == "ffill":
            df[col] = df[col].ffill()
        elif strategy == "bfill":
            df[col] = df[col].bfill()

    return df


def convert_dtype(df: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
    """target_type: 'int', 'float', 'string', 'datetime', 'category'"""
    df = df.copy()
    try:
        if target_type == "int":
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
        elif target_type == "float":
            df[column] = pd.to_numeric(df[column], errors="coerce")
        elif target_type == "string":
            df[column] = df[column].astype(str)
        elif target_type == "datetime":
            df[column] = pd.to_datetime(df[column], errors="coerce")
        elif target_type == "category":
            df[column] = df[column].astype("category")
    except Exception as e:
        raise ValueError(f"Could not convert '{column}' to {target_type}: {e}")
    return df


def remove_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    return df.drop(columns=[c for c in columns if c in df.columns])


def remove_outliers(df: pd.DataFrame, column: str) -> pd.DataFrame:
    mask = detect_outliers_iqr(df, column)
    return df[~mask].reset_index(drop=True)


def auto_clean(df: pd.DataFrame) -> pd.DataFrame:
    """One-click automatic cleaning: drop exact duplicates, fill numeric with median, categorical with mode."""
    df = remove_duplicates(df)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    if numeric_cols:
        df = handle_missing_values(df, "median", numeric_cols)
    if cat_cols:
        df = handle_missing_values(df, "mode", cat_cols)

    return df
