import pandas as pd
import streamlit as st

from config import COLORS
# ═══════════════════════════════════════════════════════
# HELPERS INTERNOS
# ═══════════════════════════════════════════════════════

def _agregar_pct(df: pd.DataFrame, col_valor: str = "valor_metrica") -> pd.DataFrame:
    out = df.copy()
    total = out[col_valor].sum()
    out["pct"] = (out[col_valor] / total * 100) if total > 0 else 0.0
    return out


def _pct_label(nombre_metrica: str) -> str:
    return "% de defunciones" if nombre_metrica == "Defunciones" else "% rel. en el grupo"


def _hover_h(val_label: str, fmt: str, pct_text: str) -> str:
    """Hovertemplate para barras horizontales."""
    return (
        f"<b>%{{y}}</b><br>"
        f"{val_label}: <b>%{{x{fmt}}}</b><br>"
        f"{pct_text}: %{{customdata[0]:.1f}}%"
        f"<extra></extra>"
    )


def _hover_v(val_label: str, fmt: str, pct_text: str) -> str:
    """Hovertemplate para barras verticales."""
    return (
        f"<b>%{{x}}</b><br>"
        f"{val_label}: <b>%{{y{fmt}}}</b><br>"
        f"{pct_text}: %{{customdata[0]:.1f}}%"
        f"<extra></extra>"
    )


def _mostrar_analisis_ia(
    datos_df: pd.DataFrame,
    titulo_grafico: str,
    style: str = "normal",
) -> None:
    """Renderiza el bloque de análisis automático por IA debajo de un gráfico."""
    from data_processing import obtener_analisis_ia

    with st.spinner("✦ Generando interpretación…"):
        respuesta = obtener_analisis_ia(datos_df, titulo_grafico)

    css_class = "ai-block-compare" if style == "compare" else "ai-block"
    icon = "◆" if style == "compare" else "✦"
    label = "Análisis Comparativo IA" if style == "compare" else "Análisis IA"
    st.markdown(
        f'<div class="{css_class}">'
        f'<strong>{icon} {label}</strong><br>'
        f'{respuesta}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _mostrar_analisis_comparativo(
    datos_a: pd.DataFrame,
    datos_b: pd.DataFrame,
    prov_a: str,
    prov_b: str,
    nombre_metrica: str,
    contexto: str = "",
) -> None:
    """Renderiza el análisis comparativo de IA entre dos provincias."""
    from data_processing import obtener_analisis_comparativo_ia

    with st.spinner(f"✦ Analizando {prov_a} vs {prov_b}…"):
        respuesta = obtener_analisis_comparativo_ia(
            datos_a, datos_b, prov_a, prov_b, nombre_metrica, contexto
        )
    st.markdown(
        f'<div class="ai-block-compare">'
        f'<strong>◆ Comparativa IA &nbsp;·&nbsp; '
        f'<span class="prov-chip-a">{prov_a}</span> vs '
        f'<span class="prov-chip-b">{prov_b}</span></strong><br>'
        f'{respuesta}'
        f'</div>',
        unsafe_allow_html=True,
    )

def render_kpi_card(label: str, value: str, subtext: str = "", color_class: str = "") -> None:
    """Renderiza una tarjeta KPI con estilo consistente."""
    st.markdown(
        f'<div class="kpi-card {color_class}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{subtext}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def render_comparison_kpi_row(label: str, val_a: float, val_b: float, prov_a: str, prov_b: str, fmt_a: str, fmt_b: str):
    """Renderiza dos tarjetas de comparación con el cálculo automático de diferencia (delta)."""
    ca, cb = st.columns(2)
    
    with ca:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val_a:{fmt_a}}</div>'
            f'<div style="margin-top:6px;"><span class="prov-chip-a">{prov_a}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    with cb:
        delta_html = ""
        if val_a > 0:
            diff_pct = ((val_b - val_a) / val_a) * 100
            if abs(diff_pct) < 2:
                delta_html = '<span class="delta-neu">≈ similar</span>'
            elif diff_pct > 0:
                delta_html = f'<span class="delta-up">▲ {diff_pct:+.1f}%</span>'
            else:
                delta_html = f'<span class="delta-down">▼ {diff_pct:+.1f}%</span>'

        st.markdown(
            f'<div class="kpi-card kpi-card-orange">'
            f'<div class="kpi-label">{label} {delta_html}</div>'
            f'<div class="kpi-value">{val_b:{fmt_b}}</div>'
            f'<div style="margin-top:6px;"><span class="prov-chip-b">{prov_b}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

def sidebar_header(title: str, subtitle: str, badge: str):
    """Renderiza el encabezado premium del sidebar."""
    st.markdown(
        f'<div class="sidebar-logo">{title}</div>'
        f'<div class="sidebar-subtitle">{subtitle}</div>'
        f'<div class="sidebar-badge">{badge}</div>',
        unsafe_allow_html=True,
    )

def custom_info_box(title: str, content: str):
    """Renderiza una caja de información con estilo consistente."""
    st.markdown(
        f'<div class="info-box"><strong>{title}</strong><br>{content}</div>',
        unsafe_allow_html=True,
    )