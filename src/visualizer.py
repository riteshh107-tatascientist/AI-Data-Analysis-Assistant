"""
visualizer.py
Interactive chart generation using Plotly, plus automatic chart recommendation.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

TEMPLATE = "plotly_dark"
COLOR_SEQUENCE = px.colors.sequential.Tealgrn


def recommend_charts(df: pd.DataFrame) -> list:
    """
    Return a list of recommended chart configs based on column types.
    Each item: {"type": ..., "title": ..., "x": ..., "y": ...}
    """
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    recs = []

    if numeric_cols:
        recs.append({"type": "histogram", "title": f"Distribution of {numeric_cols[0]}", "x": numeric_cols[0]})

    if len(numeric_cols) >= 2:
        recs.append({
            "type": "scatter", "title": f"{numeric_cols[0]} vs {numeric_cols[1]}",
            "x": numeric_cols[0], "y": numeric_cols[1]
        })
        recs.append({"type": "heatmap", "title": "Correlation Heatmap"})

    if categorical_cols and numeric_cols:
        recs.append({
            "type": "bar", "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
            "x": categorical_cols[0], "y": numeric_cols[0]
        })
        if df[categorical_cols[0]].nunique() <= 12:
            recs.append({"type": "pie", "title": f"Share of {categorical_cols[0]}", "x": categorical_cols[0]})

    if datetime_cols and numeric_cols:
        recs.append({
            "type": "line", "title": f"{numeric_cols[0]} over {datetime_cols[0]}",
            "x": datetime_cols[0], "y": numeric_cols[0]
        })

    if numeric_cols:
        recs.append({"type": "box", "title": f"Box Plot of {numeric_cols[0]}", "x": numeric_cols[0]})

    return recs


def make_chart(df: pd.DataFrame, chart_type: str, x=None, y=None, color=None, title=""):
    """Generate a Plotly figure for the given chart type."""
    df = df.copy()

    if chart_type == "bar":
        agg = df.groupby(x, dropna=False)[y].mean(numeric_only=True).reset_index().sort_values(y, ascending=False).head(20)
        fig = px.bar(agg, x=x, y=y, title=title, template=TEMPLATE, color=y, color_continuous_scale=COLOR_SEQUENCE)

    elif chart_type == "line":
        d = df.sort_values(x)
        fig = px.line(d, x=x, y=y, title=title, template=TEMPLATE)

    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, color=color, title=title, template=TEMPLATE,
                          color_continuous_scale=COLOR_SEQUENCE, opacity=0.75)

    elif chart_type == "histogram":
        fig = px.histogram(df, x=x, title=title, template=TEMPLATE, color_discrete_sequence=["#2dd4bf"])

    elif chart_type == "box":
        fig = px.box(df, y=x, title=title, template=TEMPLATE, color_discrete_sequence=["#38bdf8"])

    elif chart_type == "pie":
        vc = df[x].value_counts().reset_index()
        vc.columns = [x, "count"]
        fig = px.pie(vc, names=x, values="count", title=title, template=TEMPLATE,
                      color_discrete_sequence=px.colors.sequential.Tealgrn)

    elif chart_type == "heatmap":
        numeric_df = df.select_dtypes(include=np.number)
        corr = numeric_df.corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.columns,
            colorscale="Tealgrn", zmin=-1, zmax=1
        ))
        fig.update_layout(title=title or "Correlation Heatmap", template=TEMPLATE)

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(l=30, r=30, t=60, b=30),
        title_font=dict(size=18),
    )
    return fig
