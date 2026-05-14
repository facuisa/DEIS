"""KPIs del dashboard general."""

import pandas as pd
import streamlit as st

from src.analysis.aggregations import metric_by_province_year
from ui_utils import render_kpi_card


def show_kpis(df: pd.DataFrame, nombre_metrica: str = "Defunciones") -> None:
    n_provincias = df["provincia"].nunique()
    n_causas = df["causa_desc"].nunique()
    n_anios = df["anio"].nunique()

    if nombre_metrica == "Defunciones":
        total_val = df["valor_metrica"].sum()
        val_fmt = f"{total_val:,.0f}"
        val_label = "Total Defunciones"
        val_sub = f"promedio {total_val/max(n_anios,1):,.0f}/año"
    else:
        tasa_prov_anio = metric_by_province_year(df)["valor_metrica"]
        mediana = tasa_prov_anio.median()
        maximo = tasa_prov_anio.max()
        val_fmt = f"{mediana:,.1f}"
        val_label = "Tasa mediana c/100k"
        val_sub = f"máx. {maximo:,.1f}"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(val_label, val_fmt, val_sub)
    with c2:
        render_kpi_card("Provincias", str(n_provincias), "con datos en el período", "kpi-card-green")
    with c3:
        render_kpi_card("Causas registradas", str(n_causas), "diagnósticos distintos", "kpi-card-accent")
    with c4:
        render_kpi_card("Años con datos", str(n_anios), "serie temporal completa", "kpi-card-amber")
