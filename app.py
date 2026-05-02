"""
app.py – Punto de entrada principal del Dashboard de Mortalidad en Argentina.
DEIS 2005-2023 · Ministerio de Salud de la Nación Argentina.

Estructura del proyecto:
    app.py               ← Este archivo (orquestador)
    config.py            ← Configuración, constantes y CSS
    data_processing.py   ← Carga, transformación y filtrado de datos
    ui_components.py     ← Componentes visuales, gráficos y secciones
    data/
        mortalidad_analizada_2005_2023.parquet
"""

import streamlit as st

from config import setup_config
from data_processing import apply_filters, get_subgroup_columns, load_data
from ui_components import (
    build_sidebar,
    plot_cause_analysis,
    plot_territorial_analysis,
    plot_time_series,
    section_resumen,
    show_filtered_table,
    show_kpis,
    show_methodology_note,
)

# IMPORTANTE: setup_config() debe ser la primera llamada a Streamlit del módulo,
# ya que contiene st.set_page_config() que solo puede ejecutarse una vez y antes
# de cualquier otro comando de Streamlit.
setup_config()


def main() -> None:
    """Función principal: orquesta la carga de datos, filtros y renderizado."""

    # ── Carga de datos ────────────────────────────────────────────────────────
    df_raw = load_data()
    subgroup_cols = get_subgroup_columns(df_raw)

    # ── Sidebar con filtros globales ──────────────────────────────────────────
    filters = build_sidebar(df_raw)

    # ── Aplicar filtros ───────────────────────────────────────────────────────
    df = apply_filters(df_raw, filters)

    # ── Encabezado ────────────────────────────────────────────────────────────
    st.markdown("## 📊 Dashboard de Mortalidad en Argentina")
    st.markdown(
        "**Fuente:** DEIS · Ministerio de Salud de la Nación &nbsp;|&nbsp; "
        "**Período:** 2005–2023 &nbsp;|&nbsp; "
        "**Valores absolutos · Sin tasas**"
    )
    show_methodology_note()
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Guardia: datos vacíos ─────────────────────────────────────────────────
    if df.empty:
        st.warning(
            "⚠️ La combinación de filtros seleccionada no devuelve datos. "
            "Ajustá los filtros del sidebar."
        )
        return

    # ── KPIs ──────────────────────────────────────────────────────────────────
    show_kpis(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Sección A: Resumen general ────────────────────────────────────────────
    section_resumen(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Sección B: Análisis territorial ──────────────────────────────────────
    plot_territorial_analysis(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Sección C: Análisis por causa ─────────────────────────────────────────
    plot_cause_analysis(df, subgroup_cols)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Sección D: Serie temporal ─────────────────────────────────────────────
    plot_time_series(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Sección E: Tabla interactiva ──────────────────────────────────────────
    show_filtered_table(df)


if __name__ == "__main__":
    main()
