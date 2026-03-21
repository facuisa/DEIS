"""
Dashboard de Mortalidad en Argentina - DEIS 2005-2023
Aplicación analítica profesional para exploración de datos epidemiológicos.
Fuente: Dirección de Estadísticas e Información en Salud (DEIS), Argentina.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DEIS | Mortalidad Argentina",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de colores institucional
COLORS = {
    "primary":    "#1B4F72",
    "secondary":  "#2E86C1",
    "accent":     "#E74C3C",
    "neutral":    "#ECF0F1",
    "text_dark":  "#1C2833",
    "success":    "#1E8449",
    "warn":       "#D4AC0D",
}

PLOTLY_TEMPLATE = "plotly_white"
COLOR_SEQ = px.colors.qualitative.Set2

# CSS personalizado
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1B4F72;
    }
    [data-testid="stSidebar"] * {
        color: #ECF0F1 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #AED6F1 !important;
        font-weight: 600;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1B4F72 0%, #2E86C1 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(27, 79, 114, 0.3);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.85;
        margin-top: 4px;
    }
    .kpi-card-accent {
        background: linear-gradient(135deg, #922B21 0%, #E74C3C 100%);
    }
    .kpi-card-green {
        background: linear-gradient(135deg, #145A32 0%, #1E8449 100%);
    }

    /* Section headers */
    .section-header {
        border-left: 4px solid #2E86C1;
        padding-left: 12px;
        margin: 28px 0 16px 0;
        font-size: 1.15rem;
        font-weight: 700;
        color: #1B4F72;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Info box */
    .info-box {
        background: #EBF5FB;
        border: 1px solid #AED6F1;
        border-radius: 8px;
        padding: 14px 18px;
        font-size: 0.82rem;
        color: #1A5276;
        line-height: 1.6;
    }

    /* Divider */
    .custom-divider {
        border: none;
        border-top: 2px solid #D5D8DC;
        margin: 24px 0;
    }

    /* Hide default streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGA Y CACHÉ DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando dataset DEIS…")
def load_data() -> pd.DataFrame:
    df = pd.read_parquet(
        "data/mortalidad_analizada_2005_2023.parquet"
    )
    # Normalizar nombres de columna (strip + uppercase)
    df.columns = df.columns.str.strip()

    # Asegurarse de que CUENTA sea numérico
    df["CUENTA"] = pd.to_numeric(df["CUENTA"], errors="coerce").fillna(0).astype(int)

    # Asegurarse de que anio sea int
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")

    return df


# ─────────────────────────────────────────────
# DETECCIÓN DE COLUMNAS DE SUBGRUPOS
# ─────────────────────────────────────────────
def get_subgroup_columns(df: pd.DataFrame) -> list[str]:
    """Detecta columnas que parecen ser subgrupos de causa."""
    keywords = ["subgrupo", "subtipo", "sub_", "grupo_", "_sub"]
    return [
        c for c in df.columns
        if any(k in c.lower() for k in keywords)
    ]


# ─────────────────────────────────────────────
# APLICAR FILTROS GLOBALES
# ─────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    fdf = df.copy()

    # Rango de años
    fdf = fdf[fdf["anio"].between(filters["anio"][0], filters["anio"][1])]

    # Región
    if filters["region"] and "Todas" not in filters["region"]:
        fdf = fdf[fdf["region"].isin(filters["region"])]

    # Provincia
    if filters["provincia"] and "Todas" not in filters["provincia"]:
        fdf = fdf[fdf["provincia"].isin(filters["provincia"])]

    # Sexo
    if filters["sexo"] and "Todos" not in filters["sexo"]:
        fdf = fdf[fdf["sexo_desc"].isin(filters["sexo"])]

    # Edad
    if filters["edad"] and "Todos" not in filters["edad"]:
        fdf = fdf[fdf["EDAD_norm"].isin(filters["edad"])]

    # Causa macro
    if filters["causa_macro"] and "Todas" not in filters["causa_macro"]:
        fdf = fdf[fdf["CAUSA_grupo_macro"].isin(filters["causa_macro"])]

    return fdf


# ─────────────────────────────────────────────
# SIDEBAR – FILTROS GLOBALES
# ─────────────────────────────────────────────
def build_sidebar(df: pd.DataFrame) -> dict:
    with st.sidebar:
        st.markdown("## 🏥 DEIS Dashboard")
        st.markdown("**Mortalidad Argentina · 2005–2023**")
        st.markdown("---")

        anio_min = int(df["anio"].min())
        anio_max = int(df["anio"].max())
        anio_range = st.slider(
            "Rango de años",
            min_value=anio_min,
            max_value=anio_max,
            value=(anio_min, anio_max),
            step=1,
        )

        st.markdown("---")

        regiones = ["Todas"] + sorted(df["region"].dropna().unique().tolist())
        region_sel = st.multiselect("Región", regiones, default=["Todas"])

        provincias = ["Todas"] + sorted(df["provincia"].dropna().unique().tolist())
        prov_sel = st.multiselect("Provincia", provincias, default=["Todas"])

        st.markdown("---")

        sexos = ["Todos"] + sorted(df["sexo_desc"].dropna().unique().tolist())
        sexo_sel = st.multiselect("Sexo", sexos, default=["Todos"])

        edades = ["Todos"] + sorted(df["EDAD_norm"].dropna().unique().tolist())
        edad_sel = st.multiselect("Grupo etario", edades, default=["Todos"])

        st.markdown("---")

        causas = ["Todas"] + sorted(df["CAUSA_grupo_macro"].dropna().unique().tolist())
        causa_sel = st.multiselect("Grupo macro de causa", causas, default=["Todas"])

        st.markdown("---")
        st.markdown(
            "<div style='font-size:0.72rem; opacity:0.7;'>Fuente: DEIS, Argentina.<br>"
            "Valores absolutos. Sin tasas.</div>",
            unsafe_allow_html=True,
        )

    return {
        "anio": anio_range,
        "region": region_sel,
        "provincia": prov_sel,
        "sexo": sexo_sel,
        "edad": edad_sel,
        "causa_macro": causa_sel,
    }


# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
def show_kpis(df: pd.DataFrame):
    total_def = df["CUENTA"].sum()
    n_provincias = df["provincia"].nunique()
    n_causas = df["causa_desc"].nunique()
    n_anios = df["anio"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-value">{total_def:,.0f}</div>'
            f'<div class="kpi-label">Total de Defunciones</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="kpi-card kpi-card-green">'
            f'<div class="kpi-value">{n_provincias}</div>'
            f'<div class="kpi-label">Provincias presentes</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="kpi-card kpi-card-accent">'
            f'<div class="kpi-value">{n_causas}</div>'
            f'<div class="kpi-label">Causas registradas</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-value">{n_anios}</div>'
            f'<div class="kpi-label">Años con datos</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# SECCIÓN A – RESUMEN GENERAL
# ─────────────────────────────────────────────
def plot_top_causes(df: pd.DataFrame, n: int = 10):
    top = (
        df.groupby("causa_desc")["CUENTA"]
        .sum()
        .nlargest(n)
        .reset_index()
        .sort_values("CUENTA")
    )
    fig = px.bar(
        top,
        x="CUENTA",
        y="causa_desc",
        orientation="h",
        title=f"Top {n} causas de muerte",
        labels={"CUENTA": "Defunciones", "causa_desc": "Causa"},
        color="CUENTA",
        color_continuous_scale=["#AED6F1", "#1B4F72"],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title="",
        xaxis_title="Defunciones",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        height=400,
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Defunciones: %{x:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, width="stretch")


def plot_sex_distribution(df: pd.DataFrame):
    sex = df.groupby("sexo_desc")["CUENTA"].sum().reset_index()
    fig = px.bar(
        sex,
        x="sexo_desc",
        y="CUENTA",
        title="Defunciones por sexo",
        labels={"CUENTA": "Defunciones", "sexo_desc": "Sexo"},
        color="sexo_desc",
        color_discrete_sequence=COLOR_SEQ,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Defunciones",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Defunciones: %{y:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, width='stretch')


def plot_age_distribution(df: pd.DataFrame):
    age = (
        df.groupby("EDAD_norm")["CUENTA"]
        .sum()
        .reset_index()
        .sort_values("CUENTA", ascending=False)
    )
    fig = px.bar(
        age,
        x="EDAD_norm",
        y="CUENTA",
        title="Defunciones por grupo etario",
        labels={"CUENTA": "Defunciones", "EDAD_norm": "Grupo etario"},
        color="CUENTA",
        color_continuous_scale=["#AED6F1", "#1B4F72"],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Grupo etario",
        yaxis_title="Defunciones",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
        xaxis_tickangle=-35,
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Defunciones: %{y:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, width='stretch')


def section_resumen(df: pd.DataFrame):
    st.markdown('<div class="section-header">A · Resumen General</div>', unsafe_allow_html=True)
    plot_top_causes(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        plot_sex_distribution(df)
    with c2:
        plot_age_distribution(df)


# ─────────────────────────────────────────────
# SECCIÓN B – ANÁLISIS TERRITORIAL
# ─────────────────────────────────────────────
def plot_territorial_analysis(df: pd.DataFrame):
    st.markdown('<div class="section-header">B · Análisis Territorial</div>', unsafe_allow_html=True)

    nivel = st.radio(
        "Ver por:",
        ["Región", "Provincia"],
        horizontal=True,
        key="territorial_nivel",
    )
    col_geo = "region" if nivel == "Región" else "provincia"

    # Ranking total
    ranking = (
        df.groupby(col_geo)["CUENTA"]
        .sum()
        .reset_index()
        .sort_values("CUENTA", ascending=True)
    )
    fig_rank = px.bar(
        ranking,
        x="CUENTA",
        y=col_geo,
        orientation="h",
        title=f"Defunciones totales por {nivel.lower()}",
        labels={"CUENTA": "Defunciones", col_geo: nivel},
        color="CUENTA",
        color_continuous_scale=["#AED6F1", "#1B4F72"],
        template=PLOTLY_TEMPLATE,
    )
    fig_rank.update_layout(
        coloraxis_showscale=False,
        yaxis_title="",
        plot_bgcolor="white",
        height=max(350, len(ranking) * 28),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig_rank.update_traces(
        hovertemplate=f"<b>%{{y}}</b><br>Defunciones: %{{x:,.0f}}<extra></extra>"
    )
    st.plotly_chart(fig_rank, width='stretch')

    # Heatmap: geo x causa macro
    st.markdown("**Distribución por causa macro y territorio** *(heatmap)*")
    pivot = (
        df.groupby([col_geo, "CAUSA_grupo_macro"])["CUENTA"]
        .sum()
        .reset_index()
        .pivot(index=col_geo, columns="CAUSA_grupo_macro", values="CUENTA")
        .fillna(0)
    )
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        title=f"Defunciones por {nivel.lower()} y grupo de causa",
        labels={"color": "Defunciones"},
        template=PLOTLY_TEMPLATE,
    )
    fig_heat.update_layout(
        height=max(400, len(pivot) * 30),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_tickangle=-40,
    )
    fig_heat.update_traces(
        hovertemplate="<b>%{y}</b> · %{x}<br>Defunciones: %{z:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig_heat, width='stretch')


# ─────────────────────────────────────────────
# SECCIÓN C – ANÁLISIS POR CAUSA
# ─────────────────────────────────────────────
def plot_cause_analysis(df: pd.DataFrame, subgroup_cols: list[str]):
    st.markdown('<div class="section-header">C · Análisis por Causa</div>', unsafe_allow_html=True)

    causas_macro = sorted(df["CAUSA_grupo_macro"].dropna().unique().tolist())
    causa_sel = st.selectbox("Seleccioná un grupo macro de causa", causas_macro, key="causa_macro_sel")

    dfc = df[df["CAUSA_grupo_macro"] == causa_sel]

    c1, c2 = st.columns(2)

    # Distribución por sexo para esa causa
    with c1:
        sex_c = dfc.groupby("sexo_desc")["CUENTA"].sum().reset_index()
        fig_s = px.bar(
            sex_c,
            x="sexo_desc",
            y="CUENTA",
            title=f"Distribución por sexo · {causa_sel}",
            labels={"CUENTA": "Defunciones", "sexo_desc": "Sexo"},
            color="sexo_desc",
            color_discrete_sequence=COLOR_SEQ,
            template=PLOTLY_TEMPLATE,
        )
        fig_s.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            height=320,
            xaxis_title="",
            margin=dict(l=10, r=10, t=40, b=10),
        )
        fig_s.update_traces(
            hovertemplate="<b>%{x}</b><br>Defunciones: %{y:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig_s, width='stretch')

    # Distribución por edad para esa causa
    with c2:
        age_c = dfc.groupby("EDAD_norm")["CUENTA"].sum().reset_index()
        fig_a = px.bar(
            age_c,
            x="EDAD_norm",
            y="CUENTA",
            title=f"Distribución por edad · {causa_sel}",
            labels={"CUENTA": "Defunciones", "EDAD_norm": "Grupo etario"},
            color="CUENTA",
            color_continuous_scale=["#AED6F1", "#1B4F72"],
            template=PLOTLY_TEMPLATE,
        )
        fig_a.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white",
            height=320,
            xaxis_tickangle=-35,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        fig_a.update_traces(
            hovertemplate="<b>%{x}</b><br>Defunciones: %{y:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig_a, width='stretch')

    # Subgrupos específicos (si existen y tienen datos para esta causa)
    relevant_subs = [
        c for c in subgroup_cols
        if causa_sel.lower().replace(" ", "_") in c.lower()
        or any(k in c.lower() for k in causa_sel.lower().split())
    ]
    # Fallback: mostrar todos los subgrupos con datos no nulos en el subset
    if not relevant_subs:
        relevant_subs = [c for c in subgroup_cols if dfc[c].notna().any() and (dfc[c] != "").any()]

    if relevant_subs:
        st.markdown(f"**Subgrupos detectados para *{causa_sel}***")
        for sub_col in relevant_subs:
            sub_df = (
                dfc.groupby(sub_col)["CUENTA"]
                .sum()
                .reset_index()
                .dropna(subset=[sub_col])
                .query(f"`{sub_col}` != ''")
                .sort_values("CUENTA", ascending=True)
            )
            if sub_df.empty:
                continue
            fig_sub = px.bar(
                sub_df,
                x="CUENTA",
                y=sub_col,
                orientation="h",
                title=f"Subgrupo: {sub_col}",
                labels={"CUENTA": "Defunciones", sub_col: "Subgrupo"},
                color="CUENTA",
                color_continuous_scale=["#AED6F1", "#1B4F72"],
                template=PLOTLY_TEMPLATE,
            )
            fig_sub.update_layout(
                coloraxis_showscale=False,
                yaxis_title="",
                plot_bgcolor="white",
                height=max(300, len(sub_df) * 30),
                margin=dict(l=10, r=10, t=40, b=10),
            )
            fig_sub.update_traces(
                hovertemplate="<b>%{y}</b><br>Defunciones: %{x:,.0f}<extra></extra>"
            )
            st.plotly_chart(fig_sub, width='stretch')
    else:
        st.info("No se detectaron columnas de subgrupos específicos para esta causa.")


# ─────────────────────────────────────────────
# SECCIÓN D – SERIE TEMPORAL
# ─────────────────────────────────────────────
def plot_time_series(df: pd.DataFrame):
    st.markdown('<div class="section-header">D · Serie Temporal</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        modo = st.radio(
            "Desglosar serie por:",
            ["Sin desglose", "Grupo macro de causa", "Sexo", "Región"],
            horizontal=True,
            key="ts_modo",
        )
    with c2:
        if modo != "Sin desglose":
            max_cat = st.slider("Máximo de categorías a mostrar", 2, 10, 5, key="ts_max_cat")

    if modo == "Sin desglose":
        ts = df.groupby("anio")["CUENTA"].sum().reset_index()
        fig = px.line(
            ts,
            x="anio",
            y="CUENTA",
            title="Evolución anual de defunciones",
            labels={"CUENTA": "Defunciones", "anio": "Año"},
            markers=True,
            template=PLOTLY_TEMPLATE,
            line_shape="spline",
        )
        fig.update_traces(
            line_color=COLORS["secondary"],
            marker=dict(size=7, color=COLORS["primary"]),
            hovertemplate="Año %{x}<br>Defunciones: %{y:,.0f}<extra></extra>",
        )

    else:
        col_map = {
            "Grupo macro de causa": "CAUSA_grupo_macro",
            "Sexo": "sexo_desc",
            "Región": "region",
        }
        col = col_map[modo]

        # Top N categorías por total para no saturar
        top_cats = (
            df.groupby(col)["CUENTA"]
            .sum()
            .nlargest(max_cat)
            .index.tolist()
        )
        ts = (
            df[df[col].isin(top_cats)]
            .groupby(["anio", col])["CUENTA"]
            .sum()
            .reset_index()
        )
        fig = px.line(
            ts,
            x="anio",
            y="CUENTA",
            color=col,
            title=f"Evolución anual de defunciones por {modo.lower()}",
            labels={"CUENTA": "Defunciones", "anio": "Año", col: modo},
            markers=True,
            template=PLOTLY_TEMPLATE,
            line_shape="spline",
            color_discrete_sequence=COLOR_SEQ,
        )
        fig.update_traces(
            hovertemplate="Año %{x}<br>Defunciones: %{y:,.0f}<extra></extra>"
        )

    fig.update_layout(
        plot_bgcolor="white",
        height=420,
        xaxis=dict(dtick=1, tickangle=-45),
        yaxis_title="Defunciones",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=60, b=20),
    )
    st.plotly_chart(fig, width='stretch')

    # Stacked bar por sexo y año (siempre útil)
    if "sexo_desc" in df.columns:
        st.markdown("**Composición anual por sexo** *(barras apiladas)*")
        ts_sex = df.groupby(["anio", "sexo_desc"])["CUENTA"].sum().reset_index()
        fig2 = px.bar(
            ts_sex,
            x="anio",
            y="CUENTA",
            color="sexo_desc",
            barmode="stack",
            title="Defunciones anuales por sexo (apiladas)",
            labels={"CUENTA": "Defunciones", "anio": "Año", "sexo_desc": "Sexo"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig2.update_layout(
            plot_bgcolor="white",
            height=360,
            xaxis=dict(dtick=1, tickangle=-45),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=10, r=10, t=60, b=20),
        )
        fig2.update_traces(
            hovertemplate="Año %{x}<br>%{fullData.name}<br>Defunciones: %{y:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig2, width='stretch')


# ─────────────────────────────────────────────
# SECCIÓN E – TABLA INTERACTIVA
# ─────────────────────────────────────────────
def show_filtered_table(df: pd.DataFrame):
    st.markdown('<div class="section-header">E · Tabla de Datos Filtrados</div>', unsafe_allow_html=True)

    with st.expander("Ver tabla de datos (filtrada según selección del sidebar)", expanded=False):

        vista = st.radio(
            "Modo de vista:",
            ["Agregada por causa y año", "Registros crudos (primeros 2.000)"],
            horizontal=True,
            key="tabla_vista",
        )

        buscar = st.text_input("Buscar (provincia, causa, etc.)", key="tabla_buscar")

        if vista == "Agregada por causa y año":
            group_cols = [c for c in ["anio", "provincia", "CAUSA_grupo_macro", "causa_desc", "sexo_desc"] if c in df.columns]
            show_df = (
                df.groupby(group_cols)["CUENTA"]
                .sum()
                .reset_index()
                .sort_values(["anio", "CUENTA"], ascending=[True, False])
            )
        else:
            show_df = df.head(2_000).copy()

        if buscar:
            mask = show_df.apply(
                lambda col: col.astype(str).str.contains(buscar, case=False, na=False)
            ).any(axis=1)
            show_df = show_df[mask]

        st.caption(f"**{show_df.shape[0]:,} registros** mostrados en pantalla · El CSV descargable contiene todos los registros filtrados.")
        st.dataframe(show_df, width='stretch', height=400)

        csv_export = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar CSV filtrado completo",
            data=csv_export,
            file_name="mortalidad_filtrado.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────
# NOTA METODOLÓGICA
# ─────────────────────────────────────────────
def show_methodology_note():
    st.markdown(
        """
        <div class="info-box">
        <strong>📋 Nota metodológica</strong><br>
        <strong>Fuente:</strong> Dirección de Estadísticas e Información en Salud (DEIS), Ministerio de Salud de la Nación Argentina.<br>
        <strong>Período:</strong> 2005–2023 · <strong>Dataset:</strong> derivado analítico limpio y validado.<br>
        <strong>Unidad de análisis:</strong> la columna <code>CUENTA</code> representa cantidad de defunciones (registros agregados, no individuales).<br>
        <strong>Valores absolutos:</strong> todos los análisis se expresan en números absolutos. No se calculan tasas, porcentajes de incidencia ni prevalencia, dado que el dataset no contiene datos de población de referencia.<br>
        <strong>Advertencia:</strong> las comparaciones territoriales deben interpretarse con cautela; diferencias en volumen pueden reflejar diferencias de población y no necesariamente diferencias epidemiológicas reales.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
def main():
    # Carga
    df_raw = load_data()
    subgroup_cols = get_subgroup_columns(df_raw)

    # Sidebar → filtros
    filters = build_sidebar(df_raw)

    # Filtrado
    df = apply_filters(df_raw, filters)

    # Header
    st.markdown(
        "## 📊 Dashboard de Mortalidad en Argentina",
    )
    st.markdown(
        "**Fuente:** DEIS · Ministerio de Salud de la Nación &nbsp;|&nbsp; "
        "**Período:** 2005–2023 &nbsp;|&nbsp; "
        "**Valores absolutos · Sin tasas**"
    )
    show_methodology_note()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Guardia: datos vacíos
    if df.empty:
        st.warning("⚠️ La combinación de filtros seleccionada no devuelve datos. Ajustá los filtros del sidebar.")
        return

    # KPIs
    show_kpis(df)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Secciones
    section_resumen(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    plot_territorial_analysis(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    plot_cause_analysis(df, subgroup_cols)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    plot_time_series(df)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    show_filtered_table(df)


if __name__ == "__main__":
    main()