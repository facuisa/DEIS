"""Helpers visuales compartidos para figuras y tablas."""

import pandas as pd
import plotly.graph_objects as go

from config import COLORS


_BASE_LAYOUT = dict(
    font=dict(family="Source Sans 3, sans-serif", size=12, color=COLORS["ink"]),
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=48, b=16),
    hoverlabel=dict(
        bgcolor=COLORS["navy"],
        font_color="white",
        font_family="Source Sans 3, sans-serif",
        font_size=13,
        bordercolor=COLORS["navy"],
    ),
    title_font=dict(
        family="Source Sans 3, sans-serif",
        size=14,
        color=COLORS["navy"],
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#ECECEA",
        gridwidth=1,
        zeroline=False,
        linecolor=COLORS["warm_gray"],
        tickfont=dict(size=11, color=COLORS["stone"]),
        title_font=dict(size=12, color=COLORS["stone"]),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#ECECEA",
        gridwidth=1,
        zeroline=False,
        linecolor=COLORS["warm_gray"],
        tickfont=dict(size=11, color=COLORS["stone"]),
        title_font=dict(size=12, color=COLORS["stone"]),
    ),
    legend=dict(
        font=dict(size=11, color=COLORS["ink"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)


def _apply_base(fig: go.Figure, height: int = 400) -> go.Figure:
    """Aplica layout base premium a cualquier figura Plotly."""
    fig.update_layout(height=height, **_BASE_LAYOUT)
    return fig


def _fill_metric_na(df: pd.DataFrame, metric_cols: list[str]) -> pd.DataFrame:
    """Rellena faltantes solo en columnas métricas, no en categóricas."""
    out = df.copy()
    existing_metric_cols = [col for col in metric_cols if col in out.columns]
    if existing_metric_cols:
        out[existing_metric_cols] = out[existing_metric_cols].fillna(0)
    return out
