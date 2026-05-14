"""
ui_components.py – Componentes visuales, gráficos y secciones de la UI.
Dashboard de Mortalidad en Argentina - DEIS 2005-2023.
Diseño editorial premium: paleta Navy · Pearl · Vermillion.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from ui_utils import (
    _agregar_pct, 
    _pct_label, 
    _hover_h, 
    _hover_v, 
    _mostrar_analisis_ia, 
    _mostrar_analisis_comparativo,
    render_kpi_card,
    render_comparison_kpi_row,
    sidebar_header,    
    custom_info_box
)

from config import (
    COLOR_SEQ,
    COLOR_SEQ_COMPARE,
    COLOR_SCALE_NAVY,
    COLOR_SCALE_DIV,
    COLORS,
    COMPARE_COLORS,
    PLOTLY_TEMPLATE,
)

from src.analysis.aggregations import (
    comparison_cause_gap,
    comparison_distribution,
    comparison_table_parts,
    comparison_time_series,
    comparison_top_causes,
    comparison_treemap_data,
    distribution_by,
    subgroup_distribution,
    territorial_heatmap_data,
    territorial_ranking,
    time_series_by,
    time_series_by_sex,
    time_series_total,
)
from src.ui.dashboard_general import (
    plot_age_distribution,
    plot_sex_distribution,
    plot_top_causes,
    section_resumen,
)
from src.ui.kpis import show_kpis
from src.ui.plotting import _apply_base, _fill_metric_na
from src.ui.tables import show_filtered_table

# ═══════════════════════════════════════════════════════
# SIDEBAR – FILTROS GLOBALES
# ═══════════════════════════════════════════════════════
def build_sidebar(df: pd.DataFrame) -> dict:
    """Construye el sidebar de filtros globales con diseño premium."""
    with st.sidebar:
        # Logo / Marca
        st.markdown(
        sidebar_header("DEIS", "Mortalidad Argentina", "2005 – 2023"),
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── Rango de años ────────────────────────────────────────────────────
        anio_min = int(df["anio"].min())
        anio_max = int(df["anio"].max())
        anio_range = st.slider(
            "Período de análisis",
            min_value=anio_min,
            max_value=anio_max,
            value=(anio_min, anio_max),
            step=1,
        )
        st.markdown("---")

        # ── Filtros geográficos ──────────────────────────────────────────────
        regiones = ["Todas"] + sorted(df["region"].dropna().unique().tolist())
        region_sel = st.multiselect("Región", regiones, default=["Todas"])

        if region_sel and "Todas" not in region_sel:
            df_prov_opts = df[df["region"].isin(region_sel)]
        else:
            df_prov_opts = df
        provincias = ["Todas"] + sorted(df_prov_opts["provincia"].dropna().unique().tolist())
        prov_sel = st.multiselect("Provincia", provincias, default=["Todas"])
        st.markdown("---")

        # ── Filtros demográficos ─────────────────────────────────────────────
        sexos = ["Todos"] + sorted(df["sexo_desc"].dropna().unique().tolist())
        sexo_sel = st.multiselect("Sexo biológico", sexos, default=["Todos"])

        edades = ["Todos"] + sorted(df["EDAD_norm"].dropna().unique().tolist())
        edad_sel = st.multiselect("Grupo etario", edades, default=["Todos"])
        st.markdown("---")

        # ── Filtro por causa ─────────────────────────────────────────────────
        causas = ["Todas"] + sorted(df["CAUSA_grupo_macro"].dropna().unique().tolist())
        causa_sel = st.multiselect("Grupo de causa", causas, default=["Todas"])
        st.markdown("---")

        # ── Selector de métrica ──────────────────────────────────────────────
        st.markdown(
            '<p style="color:#B8CDD8;font-size:0.72rem;font-weight:700;'
            'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">'
            '📐 Métrica de análisis</p>',
            unsafe_allow_html=True,
        )
        metrica = st.radio(
            "Mostrar valores como:",
            options=["Defunciones absolutas", "Tasa cada 100.000 habitantes"],
            index=0,
            key="metrica_sel",
            label_visibility="collapsed",
            help=(
                "**Tasa c/100k:** proyecciones INDEC al 1° de julio de cada año "
                "(2010–2023). Tasas crudas, no ajustadas por edad. "
                "Permite comparar territorios de diferente tamaño poblacional."
            ),
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.68rem;opacity:0.55;line-height:1.5;">'
            'Fuente: DEIS · Ministerio de Salud<br>'
            'Población: INDEC proyecciones al 1/7<br>'
            'Desarrollado con Streamlit · Groq / Llama-3.3'
            '</div>',
            unsafe_allow_html=True,
        )

    return {
        "anio":        anio_range,
        "region":      region_sel,
        "provincia":   prov_sel,
        "sexo":        sexo_sel,
        "edad":        edad_sel,
        "causa_macro": causa_sel,
        "metrica":     metrica,
    }


# ═══════════════════════════════════════════════════════
# SECCIÓN B – ANÁLISIS TERRITORIAL
# ═══════════════════════════════════════════════════════
def plot_territorial_analysis(
    df: pd.DataFrame,
    nombre_metrica: str = "Defunciones",
    fmt: str = ":,.0f",
) -> None:
    st.markdown(
        '<div class="section-header">B · Análisis Territorial</div>',
        unsafe_allow_html=True,
    )
    pct_txt = _pct_label(nombre_metrica)

    nivel = st.radio("Ver por:", ["Región", "Provincia"], horizontal=True, key="territorial_nivel")
    col_geo = "region" if nivel == "Región" else "provincia"

    ranking = territorial_ranking(df, col_geo)
    ranking = _agregar_pct(ranking)

    fig_rank = px.bar(
        ranking, x="valor_metrica", y=col_geo, orientation="h",
        title=f"{nombre_metrica} por {nivel.lower()}",
        labels={"valor_metrica": nombre_metrica, col_geo: ""},
        color="valor_metrica",
        color_continuous_scale=COLOR_SCALE_NAVY,
        template=PLOTLY_TEMPLATE,
        custom_data=["pct"],
    )
    h_rank = max(350, len(ranking) * 30)
    fig_rank.update_layout(coloraxis_showscale=False)
    _apply_base(fig_rank, height=h_rank)
    fig_rank.update_traces(
        hovertemplate=_hover_h(nombre_metrica, fmt, pct_txt),
        marker_line_width=0,
    )
    st.plotly_chart(fig_rank, use_container_width=True)
    _mostrar_analisis_ia(ranking, f"{nombre_metrica} por {nivel.lower()}")

    # Heatmap
    st.markdown(
        f'<p style="font-size:0.85rem;color:{COLORS["stone"]};font-weight:600;'
        f'margin:20px 0 8px;">Distribución por causa macro y {nivel.lower()} · heatmap</p>',
        unsafe_allow_html=True,
    )
    pivot_src, pivot, pivot_resumen = territorial_heatmap_data(df, col_geo)
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=COLOR_SCALE_NAVY,
        aspect="auto",
        title=f"{nombre_metrica} por {nivel.lower()} y grupo de causa",
        labels={"color": nombre_metrica},
        template=PLOTLY_TEMPLATE,
    )
    h_heat = max(400, len(pivot) * 32)
    _apply_base(fig_heat, height=h_heat)
    fig_heat.update_layout(xaxis_tickangle=-40)
    fig_heat.update_traces(
        hovertemplate=f"<b>%{{y}}</b> · %{{x}}<br>{nombre_metrica}: <b>%{{z{fmt}}}</b><extra></extra>"
    )
    st.plotly_chart(fig_heat, use_container_width=True)


    _mostrar_analisis_ia(
        pivot_resumen,
        f"{nombre_metrica} por {nivel.lower()} y grupo de causa",
    )


# ═══════════════════════════════════════════════════════
# SECCIÓN C – ANÁLISIS POR CAUSA
# ═══════════════════════════════════════════════════════
def plot_cause_analysis(
    df: pd.DataFrame,
    subgroup_cols: list[str],
    nombre_metrica: str = "Defunciones",
    fmt: str = ":,.0f",
) -> None:
    st.markdown(
        '<div class="section-header">C · Análisis por Causa</div>',
        unsafe_allow_html=True,
    )
    pct_txt = _pct_label(nombre_metrica)

    causas_macro = sorted(df["CAUSA_grupo_macro"].dropna().unique().tolist())
    causa_sel = st.selectbox(
        "Seleccioná un grupo macro de causa", causas_macro, key="causa_macro_sel"
    )
    dfc = df[df["CAUSA_grupo_macro"] == causa_sel]

    c1, c2 = st.columns(2)
    with c1:
        sex_c = distribution_by(dfc, "sexo_desc")
        sex_c = _agregar_pct(sex_c)
        fig_s = px.bar(
            sex_c, x="sexo_desc", y="valor_metrica",
            title=f"{nombre_metrica} por sexo · {causa_sel}",
            labels={"valor_metrica": nombre_metrica, "sexo_desc": ""},
            color="sexo_desc",
            color_discrete_sequence=COLOR_SEQ,
            template=PLOTLY_TEMPLATE,
            custom_data=["pct"],
        )
        fig_s.update_layout(showlegend=False)
        _apply_base(fig_s, height=320)
        fig_s.update_traces(
            hovertemplate=_hover_v(nombre_metrica, fmt, pct_txt),
            marker_line_width=0,
            width=0.55,
        )
        st.plotly_chart(fig_s, use_container_width=True)
        _mostrar_analisis_ia(sex_c, f"{nombre_metrica} por sexo · {causa_sel}")

    with c2:
        age_c = distribution_by(dfc, "EDAD_norm")
        age_c = _agregar_pct(age_c)
        fig_a = px.bar(
            age_c, x="EDAD_norm", y="valor_metrica",
            title=f"{nombre_metrica} por edad · {causa_sel}",
            labels={"valor_metrica": nombre_metrica, "EDAD_norm": ""},
            color="valor_metrica",
            color_continuous_scale=COLOR_SCALE_NAVY,
            template=PLOTLY_TEMPLATE,
            custom_data=["pct"],
        )
        fig_a.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        _apply_base(fig_a, height=320)
        fig_a.update_traces(
            hovertemplate=_hover_v(nombre_metrica, fmt, pct_txt),
            marker_line_width=0,
        )
        st.plotly_chart(fig_a, use_container_width=True)
        _mostrar_analisis_ia(age_c, f"{nombre_metrica} por edad · {causa_sel}")

    # Subgrupos
    relevant_subs = [
        c for c in subgroup_cols
        if causa_sel.lower().replace(" ", "_") in c.lower()
        or any(k in c.lower() for k in causa_sel.lower().split())
    ]
    if not relevant_subs:
        relevant_subs = [
            c for c in subgroup_cols
            if dfc[c].notna().any() and (dfc[c] != "").any()
        ]

    if relevant_subs:
        st.markdown(
            f'<p style="font-size:0.85rem;color:{COLORS["stone"]};font-weight:600;'
            f'margin:20px 0 8px;">Subgrupos detectados para <em>{causa_sel}</em></p>',
            unsafe_allow_html=True,
        )
        for sub_col in relevant_subs:
            sub_df = subgroup_distribution(dfc, sub_col)
            if sub_df.empty:
                continue
            sub_df = _agregar_pct(sub_df)
            fig_sub = px.bar(
                sub_df, x="valor_metrica", y=sub_col, orientation="h",
                title=f"Subgrupo: {sub_col} · {nombre_metrica}",
                labels={"valor_metrica": nombre_metrica, sub_col: ""},
                color="valor_metrica",
                color_continuous_scale=COLOR_SCALE_NAVY,
                template=PLOTLY_TEMPLATE,
                custom_data=["pct"],
            )
            fig_sub.update_layout(coloraxis_showscale=False)
            _apply_base(fig_sub, height=max(300, len(sub_df) * 30))
            fig_sub.update_traces(
                hovertemplate=_hover_h(nombre_metrica, fmt, pct_txt),
                marker_line_width=0,
            )
            st.plotly_chart(fig_sub, use_container_width=True)
            _mostrar_analisis_ia(sub_df, f"Subgrupo: {sub_col} · {causa_sel}")
    else:
        st.info("No se detectaron columnas de subgrupos específicos para esta causa.")


# ═══════════════════════════════════════════════════════
# SECCIÓN D – SERIE TEMPORAL
# ═══════════════════════════════════════════════════════
def plot_time_series(
    df: pd.DataFrame,
    nombre_metrica: str = "Defunciones",
    fmt: str = ":,.0f",
) -> None:
    st.markdown(
        '<div class="section-header">D · Evolución Temporal</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        modo = st.radio(
            "Desglosar por:",
            ["Sin desglose", "Grupo macro de causa", "Sexo", "Región"],
            horizontal=True,
            key="ts_modo",
        )
    with c2:
        if modo != "Sin desglose":
            max_cat = st.slider("Categorías", 2, 10, 5, key="ts_max_cat")

    if modo == "Sin desglose":
        ts = time_series_total(df)
        fig = px.line(
            ts, x="anio", y="valor_metrica",
            title=f"Evolución anual · {nombre_metrica}",
            labels={"valor_metrica": nombre_metrica, "anio": ""},
            markers=True,
            template=PLOTLY_TEMPLATE,
            line_shape="spline",
        )
        fig.update_traces(
            line=dict(color=COLORS["cobalt"], width=2.5),
            marker=dict(size=7, color=COLORS["navy"], line=dict(color="white", width=1.5)),
            hovertemplate=f"Año <b>%{{x}}</b><br>{nombre_metrica}: <b>%{{y{fmt}}}</b><extra></extra>",
            fill="tozeroy",
            fillcolor=f"rgba(26,111,168,0.07)",
        )
    else:
        col_map = {
            "Grupo macro de causa": "CAUSA_grupo_macro",
            "Sexo": "sexo_desc",
            "Región": "region",
        }
        col = col_map[modo]
        ts = time_series_by(df, col, max_cat)
        fig = px.line(
            ts, x="anio", y="valor_metrica", color=col,
            title=f"Evolución anual · {nombre_metrica} por {modo.lower()}",
            labels={"valor_metrica": nombre_metrica, "anio": "", col: modo},
            markers=True,
            template=PLOTLY_TEMPLATE,
            line_shape="spline",
            color_discrete_sequence=COLOR_SEQ,
        )
        fig.update_traces(
            line_width=2.2,
            marker=dict(size=6, line=dict(color="white", width=1)),
            hovertemplate=f"<b>%{{fullData.name}}</b><br>%{{x}} · {nombre_metrica}: <b>%{{y{fmt}}}</b><extra></extra>",
        )

    fig.update_layout(
        xaxis=dict(dtick=1, tickangle=-45),
        yaxis_title=nombre_metrica,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    _apply_base(fig, height=440)
    st.plotly_chart(fig, use_container_width=True)
    _mostrar_analisis_ia(
        ts,
        f"Evolución anual · {nombre_metrica} ({modo if modo != 'Sin desglose' else 'total'})",
    )

    # Stacked bar por sexo
    if "sexo_desc" in df.columns and modo != "Sexo":
        n_sexos = df["sexo_desc"].nunique()
        if n_sexos > 1:
            st.markdown(
                f'<p style="font-size:0.85rem;color:{COLORS["stone"]};font-weight:600;'
                f'margin:20px 0 8px;">{nombre_metrica} anual por sexo · barras apiladas</p>',
                unsafe_allow_html=True,
            )
            ts_sex = time_series_by_sex(df)
            fig2 = px.bar(
                ts_sex, x="anio", y="valor_metrica", color="sexo_desc",
                barmode="stack",
                title=f"{nombre_metrica} anuales por sexo",
                labels={"valor_metrica": nombre_metrica, "anio": "", "sexo_desc": "Sexo"},
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=COLOR_SEQ,
            )
            fig2.update_layout(
                xaxis=dict(dtick=1, tickangle=-45),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            _apply_base(fig2, height=360)
            fig2.update_traces(
                hovertemplate=f"<b>%{{x}}</b> · %{{fullData.name}}<br>{nombre_metrica}: <b>%{{y{fmt}}}</b><extra></extra>",
                marker_line_width=0,
            )
            st.plotly_chart(fig2, use_container_width=True)
            _mostrar_analisis_ia(ts_sex, f"{nombre_metrica} anuales por sexo (apiladas)")


# ═══════════════════════════════════════════════════════
# NOTA METODOLÓGICA
# ═══════════════════════════════════════════════════════
def show_methodology_note(nombre_metrica: str = "Defunciones") -> None:
    if nombre_metrica == "Defunciones":
        nota = (
            "Valores absolutos de defunciones. Las comparaciones territoriales deben "
            "considerar el tamaño poblacional de cada jurisdicción."
        )
    else:
        nota = (
            "Tasa cada 100.000 hab. (proyecciones INDEC 1° de julio). Tasas crudas, "
            "no ajustadas por edad. Permite comparar territorios de diferente tamaño."
        )

    content = (
        f"Fuente: DEIS, Ministerio de Salud (2005–2023).<br>"
        f"Población: INDEC 2010–2023.<br>{nota}"
    )
    custom_info_box("📋 Nota metodológica", content)


# ═══════════════════════════════════════════════════════════════════════
# MÓDULO F – COMPARATIVO TERRITORIAL ⚖️
# ═══════════════════════════════════════════════════════════════════════

def plot_comparative_analysis(
    df_raw: pd.DataFrame,
    df_poblacion: pd.DataFrame,
    filters: dict,
) -> None:
    """Módulo F – Comparativo Territorial entre dos provincias."""
    st.markdown('<div class="section-header">⚖️ Comparativo Territorial de Provincias</div>', unsafe_allow_html=True)

    metrica_activa = filters.get("metrica", "Defunciones absolutas")
    
    # ── Selectores de provincias ──────────────────────────────────────────────
    provincias_disponibles = sorted(df_raw["provincia"].dropna().unique().tolist())

    cc1, cc2, cc3 = st.columns([2, 2, 2])
    with cc1:
        prov_a = st.selectbox("🔵 Provincia A", provincias_disponibles, index=0, key="comp_prov_a")
    with cc2:
        default_b = 1 if len(provincias_disponibles) > 1 else 0
        prov_b = st.selectbox("🟠 Provincia B", provincias_disponibles, index=default_b, key="comp_prov_b")
    with cc3:
        causas_disp = ["Todas"] + sorted(df_raw["CAUSA_grupo_macro"].dropna().unique().tolist())
        causa_comp = st.selectbox("Causa macro (opcional)", causas_disp, index=0, key="comp_causa")

    if prov_a == prov_b:
        st.warning("⚠️ Seleccioná dos provincias distintas para comparar.")
        return

    # ── Cargar y calcular datos ─────────────────────────────────────────────
    from data_processing import calcular_metrica_provincia

    df_a, nm_a, fmt_a, adv_a = calcular_metrica_provincia(df_raw, df_poblacion, filters, metrica_activa, prov_a)
    df_b, nm_b, fmt_b, adv_b = calcular_metrica_provincia(df_raw, df_poblacion, filters, metrica_activa, prov_b)

    if causa_comp != "Todas":
        df_a = df_a[df_a["CAUSA_grupo_macro"] == causa_comp]
        df_b = df_b[df_b["CAUSA_grupo_macro"] == causa_comp]

    if df_a.empty or df_b.empty:
        st.warning("⚠️ Sin datos para comparar con los filtros actuales.")
        return

    nombre_metrica = nm_a
    fmt = fmt_a

    # ── KPIs comparativos ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header-compare">KPIs comparativos</div>', unsafe_allow_html=True)

    total_a = df_a["valor_metrica"].sum()
    total_b = df_b["valor_metrica"].sum()
    n_causas_a = df_a["causa_desc"].nunique()
    n_causas_b = df_b["causa_desc"].nunique()

    render_comparison_kpi_row(
        nombre_metrica + " total", total_a, total_b, prov_a, prov_b,
        ",.0f" if nombre_metrica == "Defunciones" else ",.2f",
        ",.0f" if nombre_metrica == "Defunciones" else ",.2f"
    )

    render_comparison_kpi_row(
        "Causas distintas", float(n_causas_a), float(n_causas_b), 
        prov_a, prov_b, ".0f", ".0f"
    )

    if nombre_metrica != "Defunciones":
        tasa_anual_a = time_series_total(df_a)["valor_metrica"].mean()
        tasa_anual_b = time_series_total(df_b)["valor_metrica"].mean()
        st.markdown("<br>", unsafe_allow_html=True)
        render_comparison_kpi_row("Tasa promedio anual c/100k", tasa_anual_a, tasa_anual_b, prov_a, prov_b, ",.2f", ",.2f")

    st.divider()

    # ── Gráfico Evolución ───────────────────────────────────────────────────
    ts_comp = comparison_time_series(df_a, df_b, prov_a, prov_b)

    fig_ts = px.line(ts_comp, x="anio", y="valor_metrica", color="provincia", 
                     title=f"Evolución anual · {nombre_metrica}", markers=True, template=PLOTLY_TEMPLATE)
    _apply_base(fig_ts, height=420)
    st.plotly_chart(fig_ts, width="stretch")

    st.divider()

    # ── Gráfico 2 – Top causas ────────────────────────────────────────────────
    st.markdown('<div class="section-header-compare">2 · Principales Causas de Muerte</div>', unsafe_allow_html=True)

    n_top = st.slider("Número de causas a comparar", 5, 20, 10, key="comp_n_causas")

    top_a = comparison_top_causes(df_a, prov_a, n_top)
    top_b = comparison_top_causes(df_b, prov_b, n_top)

    c1, c2 = st.columns(2)
    with c1:
        top_a_pct = _agregar_pct(top_a)
        fig_ca = px.bar(top_a_pct, x="valor_metrica", y="causa_desc", orientation="h",
                        title=f"Top {n_top} causas · {prov_a}", color_discrete_sequence=["#1A6FA8"])
        _apply_base(fig_ca, height=max(340, n_top * 34))
        fig_ca.update_traces(hovertemplate=_hover_h(nombre_metrica, fmt, _pct_label(nombre_metrica)), customdata=top_a_pct[["pct"]])
        st.plotly_chart(fig_ca, width="stretch")

    with c2:
        top_b_pct = _agregar_pct(top_b)
        fig_cb = px.bar(top_b_pct, x="valor_metrica", y="causa_desc", orientation="h",
                        title=f"Top {n_top} causas · {prov_b}", color_discrete_sequence=["#ED7D31"])
        _apply_base(fig_cb, height=max(340, n_top * 34))
        fig_cb.update_traces(hovertemplate=_hover_h(nombre_metrica, fmt, _pct_label(nombre_metrica)), customdata=top_b_pct[["pct"]])
        st.plotly_chart(fig_cb, width="stretch")

    # ── Gráfico de Brechas ────────────────────────────────────────────────────
    st.markdown(f'<p style="font-size:0.85rem;color:#666;font-weight:600;margin-top:20px;">Brecha entre provincias por causa</p>', unsafe_allow_html=True)
    
    merge_causas = comparison_cause_gap(top_a, top_b, prov_a, prov_b)
    if not merge_causas.empty:

        fig_brecha = px.bar(merge_causas, x="brecha", y="causa_desc", orientation="h",
                            title=f"Brecha {prov_b} vs {prov_a}", color="brecha",
                            color_continuous_scale="RdBu_r", color_continuous_midpoint=0)
        _apply_base(fig_brecha, height=max(340, len(merge_causas) * 30))
        st.plotly_chart(fig_brecha, width="stretch")
    else:
        st.info("No hay causas comunes suficientes en el Top para calcular brechas.")
        st.divider()

    # ── Gráfico 3 – Distribución por Sexo ────────────────────────────────────
    st.markdown('<div class="section-header-compare">3 · Distribución por Sexo</div>', unsafe_allow_html=True)

    sex_comp = comparison_distribution(df_a, df_b, "sexo_desc", prov_a, prov_b)

    fig_sex = px.bar(sex_comp, x="sexo_desc", y="valor_metrica", color="provincia",
                     barmode="group", title=f"{nombre_metrica} por sexo · comparativo",
                     color_discrete_map={prov_a: "#1A6FA8", prov_b: "#ED7D31"})
    _apply_base(fig_sex, height=360)
    fig_sex.update_traces(width=0.35, hovertemplate=f"<b>%{{fullData.name}}</b><br>%{{x}} · {nombre_metrica}: <b>%{{y{fmt}}}</b><extra></extra>")
    st.plotly_chart(fig_sex, width="stretch")

    st.divider()

    # ── Gráfico 4 – Distribución por Edad ────────────────────────────────────
    st.markdown('<div class="section-header-compare">4 · Distribución por Grupo Etario</div>', unsafe_allow_html=True)

    age_comp = comparison_distribution(df_a, df_b, "EDAD_norm", prov_a, prov_b)

    fig_age = px.bar(age_comp, x="EDAD_norm", y="valor_metrica", color="provincia",
                     barmode="group", title=f"{nombre_metrica} por grupo etario · comparativo",
                     color_discrete_map={prov_a: "#1A6FA8", prov_b: "#ED7D31"})
    fig_age.update_layout(xaxis_tickangle=-35)
    _apply_base(fig_age, height=380)
    st.plotly_chart(fig_age, width="stretch")

    st.divider()

    # ── Gráfico 5 – Treemap Proporcional ──────────────────────────────────────
    st.markdown('<div class="section-header-compare">5 · Mapa Proporcional de Causas</div>', unsafe_allow_html=True)
    
    treemap_comp = comparison_treemap_data(df_a, df_b, prov_a, prov_b)

    fig_tree = px.treemap(treemap_comp, path=["provincia", "CAUSA_grupo_macro", "causa_desc"], 
                          values="valor_metrica", color="valor_metrica",
                          color_continuous_scale="Blues", title=f"Distribución proporcional de causas")
    fig_tree.update_layout(height=520, coloraxis_showscale=False)
    st.plotly_chart(fig_tree, width="stretch")

    # ── Tabla Comparativa Final ──────────────────────────────────────────────
    st.markdown('<div class="section-header-compare">6 · Tabla Comparativa</div>', unsafe_allow_html=True)
    with st.expander("Ver tabla comparativa detallada", expanded=False):
        group_cols = [c for c in ["anio", "CAUSA_grupo_macro", "causa_desc"] if c in df_a.columns]
        
        # Agrupamos solo por la métrica para evitar conflictos de columnas duplicadas
        tbl_a, tbl_b = comparison_table_parts(
            df_a, df_b, group_cols, nombre_metrica, prov_a, prov_b
        )
        
        tbl_comp = tbl_a.merge(tbl_b, on=group_cols, how="outer")
        col_a, col_b = f"{nombre_metrica}_{prov_a}", f"{nombre_metrica}_{prov_b}"
        tbl_comp = _fill_metric_na(tbl_comp, [col_a, col_b])
        
        tbl_comp["diferencia"] = tbl_comp[col_b].astype(float) - tbl_comp[col_a].astype(float)
        tbl_comp = tbl_comp.sort_values("diferencia", key=abs, ascending=False)

        st.dataframe(tbl_comp, width="stretch", height=400)