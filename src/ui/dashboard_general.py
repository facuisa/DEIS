"""Secciones iniciales del dashboard general."""

import pandas as pd
import plotly.express as px
import streamlit as st

from config import COLOR_SCALE_NAVY, COLOR_SEQ, PLOTLY_TEMPLATE
from src.analysis.aggregations import distribution_by, top_causes
from src.ui.plotting import _apply_base
from ui_utils import _agregar_pct, _hover_h, _hover_v, _mostrar_analisis_ia, _pct_label


def plot_top_causes(
    df: pd.DataFrame,
    nombre_metrica: str = "Defunciones",
    fmt: str = ":,.0f",
    n: int = 10,
) -> None:
    pct_txt = _pct_label(nombre_metrica)
    top = top_causes(df, n)
    top = _agregar_pct(top)

    fig = px.bar(
        top, x="valor_metrica", y="causa_desc", orientation="h",
        title=f"Top {n} causas · {nombre_metrica}",
        labels={"valor_metrica": nombre_metrica, "causa_desc": ""},
        color="valor_metrica",
        color_continuous_scale=COLOR_SCALE_NAVY,
        template=PLOTLY_TEMPLATE,
        custom_data=["pct"],
    )
    fig.update_layout(
        coloraxis_showscale=False,
        height=max(380, n * 36),
        yaxis=dict(tickfont=dict(size=11)),
    )
    _apply_base(fig, height=max(380, n * 36))
    fig.update_traces(
        hovertemplate=_hover_h(nombre_metrica, fmt, pct_txt),
        marker_line_width=0,
    )
    st.plotly_chart(fig, use_container_width=True)
    _mostrar_analisis_ia(top, f"Top {n} causas · {nombre_metrica}")


def plot_sex_distribution(
    df: pd.DataFrame,
    nombre_metrica: str = "Defunciones",
    fmt: str = ":,.0f",
) -> None:
    pct_txt = _pct_label(nombre_metrica)
    sex = distribution_by(df, "sexo_desc")
    sex = _agregar_pct(sex)

    fig = px.bar(
        sex, x="sexo_desc", y="valor_metrica",
        title=f"{nombre_metrica} por sexo",
        labels={"valor_metrica": nombre_metrica, "sexo_desc": ""},
        color="sexo_desc",
        color_discrete_sequence=COLOR_SEQ,
        template=PLOTLY_TEMPLATE,
        custom_data=["pct"],
    )
    fig.update_layout(showlegend=False)
    _apply_base(fig, height=320)
    fig.update_traces(
        hovertemplate=_hover_v(nombre_metrica, fmt, pct_txt),
        marker_line_width=0,
        width=0.55,
    )
    st.plotly_chart(fig, use_container_width=True)
    _mostrar_analisis_ia(sex, f"{nombre_metrica} por sexo")


def plot_age_distribution(
    df: pd.DataFrame,
    nombre_metrica: str = "Defunciones",
    fmt: str = ":,.0f",
) -> None:
    pct_txt = _pct_label(nombre_metrica)
    age = distribution_by(df, "EDAD_norm", sort_desc=True)
    age = _agregar_pct(age)

    fig = px.bar(
        age, x="EDAD_norm", y="valor_metrica",
        title=f"{nombre_metrica} por grupo etario",
        labels={"valor_metrica": nombre_metrica, "EDAD_norm": ""},
        color="valor_metrica",
        color_continuous_scale=COLOR_SCALE_NAVY,
        template=PLOTLY_TEMPLATE,
        custom_data=["pct"],
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-35,
    )
    _apply_base(fig, height=320)
    fig.update_traces(
        hovertemplate=_hover_v(nombre_metrica, fmt, pct_txt),
        marker_line_width=0,
    )
    st.plotly_chart(fig, use_container_width=True)
    _mostrar_analisis_ia(age, f"{nombre_metrica} por grupo etario")


def section_resumen(df: pd.DataFrame, nombre_metrica: str = "Defunciones", fmt: str = ":,.0f") -> None:
    st.markdown('<div class="section-header">A · Resumen General</div>', unsafe_allow_html=True)

    plot_top_causes(df, nombre_metrica, fmt)

    st.divider() # <--- Reemplaza el div custom por el nativo de Streamlit si prefieres limpieza

    c1, c2 = st.columns(2)
    with c1:
        plot_sex_distribution(df, nombre_metrica, fmt)
    with c2:
        plot_age_distribution(df, nombre_metrica, fmt)
