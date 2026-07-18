"""
analyzer.py
Dataset profiling, descriptive statistics, and correlation analysis.
"""

import pandas as pd
import numpy as np


def profile_dataset(df: pd.DataFrame) -> dict:
    """Return a full profiling summary of the dataset."""
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist()

    # Detect columns that look like dates but weren't parsed as such
    for col in categorical_cols[:]:
        if df[col].dropna().empty:
            continue
        sample = df[col].dropna().astype(str).head(20)
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() > 0.8:
                datetime_cols.append(col)
                categorical_cols.remove(col)
        except Exception:
            pass

    return {
        "shape": df.shape,
        "n_rows": df.shape[0],
        "n_columns": df.shape[1],
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "missing_values": df.isna().sum().to_dict(),
        "unique_values": df.nunique().to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics (mean, median, mode, std, etc.) for numeric columns."""
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.empty:
        return pd.DataFrame()

    stats = numeric_df.describe().T
    stats["median"] = numeric_df.median()
    mode_vals = numeric_df.mode().iloc[0] if not numeric_df.mode().empty else np.nan
    stats["mode"] = mode_vals
    stats["skewness"] = numeric_df.skew()
    stats["missing"] = numeric_df.isna().sum()

    stats = stats.rename(columns={"50%": "median_(50%)", "std": "std_dev"})
    cols_order = ["count", "mean", "median", "mode", "std_dev", "min", "max", "skewness", "missing"]
    cols_order = [c for c in cols_order if c in stats.columns]
    return stats[cols_order].round(3)


def categorical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary table for categorical columns: unique count, top value, frequency."""
    cat_df = df.select_dtypes(include=["object", "category"])
    if cat_df.empty:
        return pd.DataFrame()

    rows = []
    for col in cat_df.columns:
        vc = cat_df[col].value_counts()
        rows.append({
            "column": col,
            "unique_values": cat_df[col].nunique(),
            "top_value": vc.index[0] if not vc.empty else None,
            "top_frequency": int(vc.iloc[0]) if not vc.empty else 0,
            "missing": int(cat_df[col].isna().sum()),
        })
    return pd.DataFrame(rows).set_index("column")


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return pd.DataFrame()
    return numeric_df.corr().round(3)


def top_correlations(df: pd.DataFrame, n: int = 5) -> list:
    """Return the top N strongest correlations (excluding self-correlation)."""
    corr = correlation_matrix(df)
    if corr.empty:
        return []

    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.iloc[i, j]
            if pd.notna(val):
                pairs.append((cols[i], cols[j], val))

    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    return pairs[:n]


def build_ai_context_summary(df: pd.DataFrame, max_cols: int = 25) -> str:
    """
    Build a compact text summary of the dataset for use as LLM context.
    Never sends raw row-level data unless explicitly small; focuses on aggregates.
    """
    profile = profile_dataset(df)
    stats = summary_statistics(df)
    cat_summary = categorical_summary(df)
    top_corr = top_correlations(df, 5)

    lines = []
    lines.append(f"Dataset shape: {profile['n_rows']} rows x {profile['n_columns']} columns")
    lines.append(f"Numeric columns: {', '.join(profile['numeric_columns'][:max_cols]) or 'None'}")
    lines.append(f"Categorical columns: {', '.join(profile['categorical_columns'][:max_cols]) or 'None'}")
    lines.append(f"Datetime columns: {', '.join(profile['datetime_columns'][:max_cols]) or 'None'}")
    lines.append(f"Duplicate rows: {profile['duplicate_rows']}")
    total_missing = sum(profile['missing_values'].values())
    lines.append(f"Total missing values: {total_missing}")

    if not stats.empty:
        lines.append("\nNumeric summary statistics:")
        lines.append(stats.to_string())

    if not cat_summary.empty:
        lines.append("\nCategorical summary:")
        lines.append(cat_summary.to_string())

    if top_corr:
        lines.append("\nTop correlations:")
        for a, b, v in top_corr:
            lines.append(f"  {a} vs {b}: {v}")

    return "\n".join(lines)
