"""
app.py – Punto de entrada principal del Dashboard de Mortalidad en Argentina.
DEIS 2005-2023 · Ministerio de Salud de la Nación Argentina.

Estructura del proyecto:
    app.py               ← Este archivo (orquestador)
    config.py            ← Sistema de diseño, colores, tipografía y CSS
    data_processing.py   ← Carga, transformación, filtrado y cálculo de métricas
    ui_components.py     ← Componentes visuales, gráficos y secciones
    data/
        mortalidad_analizada_2005_2023.parquet
        poblacion_indec_provincias_2010_2023_normalizada.parquet
"""

import streamlit as st

from config import setup_config, COLORS
from data_processing import (
    apply_filters,
    calcular_metrica,
    get_subgroup_columns,
    load_data,
    load_poblacion,
)
from ui_components import (
    build_sidebar,
    plot_cause_analysis,
    plot_comparative_analysis,
    plot_territorial_analysis,
    plot_time_series,
    section_resumen,
    show_filtered_table,
    show_kpis,
    show_methodology_note,
)

# IMPORTANTE: primera llamada a Streamlit del módulo.
setup_config()


def _render_main_header(metrica: str) -> None:
    """Renderiza el encabezado editorial principal."""
    metrica_label = "Defunciones absolutas" if "absol" in metrica.lower() else "Tasa c/100.000 hab."
    st.markdown(
        f"""
        <div style="padding: 8px 0 4px;">
            <p class="main-subheader">Ministerio de Salud · DEIS · República Argentina</p>
            <h1 class="main-header">Mortalidad en Argentina</h1>
            <p style="font-size:0.9rem; color:{COLORS['stone']}; margin-top:6px; font-family:'Source Sans 3',sans-serif;">
                Estadísticas vitales 2005–2023 &nbsp;·&nbsp; 24 provincias &nbsp;·&nbsp;
                <strong style="color:{COLORS['cobalt']};">{metrica_label}</strong>
            </p>
        </div>
        <hr class="header-rule">
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Orquesta la carga de datos, filtros y renderizado por pestaña."""

    # ── Carga de datos (cacheados) ────────────────────────────────────────────
    df_raw        = load_data()
    df_poblacion  = load_poblacion()
    subgroup_cols = get_subgroup_columns(df_raw)

    # ── Sidebar con filtros globales y selector de métrica ────────────────────
    filters  = build_sidebar(df_raw)
    metrica  = filters["metrica"]

    # ── Encabezado global ─────────────────────────────────────────────────────
    _render_main_header(metrica)

    # ── Pestañas principales ──────────────────────────────────────────────────
    tab_dash, tab_comp = st.tabs(
        ["📊  Dashboard General", "⚖️  Comparativo Territorial"]
    )

    # ══════════════════════════════════════════════════════
    # PESTAÑA 1 – DASHBOARD GENERAL
    # ══════════════════════════════════════════════════════
    with tab_dash:

        # Aplicar filtros y calcular métrica
        df_filtrado = apply_filters(df_raw, filters)
        df, nombre_metrica, fmt_metrica, advertencias = calcular_metrica(
            df_filtrado, df_poblacion, filters, metrica
        )

        show_methodology_note(nombre_metrica)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        for adv in advertencias:
            st.warning(adv)

        if df.empty:
            st.warning(
                "⚠️ La combinación de filtros seleccionada no devuelve datos. "
                "Ajustá los filtros del sidebar."
            )
        else:
            show_kpis(df, nombre_metrica)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            section_resumen(df, nombre_metrica, fmt_metrica)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            plot_territorial_analysis(df, nombre_metrica, fmt_metrica)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            plot_cause_analysis(df, subgroup_cols, nombre_metrica, fmt_metrica)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            plot_time_series(df, nombre_metrica, fmt_metrica)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            show_filtered_table(df, nombre_metrica)

    # ══════════════════════════════════════════════════════
    # PESTAÑA 2 – COMPARATIVO TERRITORIAL
    # ══════════════════════════════════════════════════════
    with tab_comp:
        plot_comparative_analysis(df_raw, df_poblacion, filters)


if __name__ == "__main__":
    main()
