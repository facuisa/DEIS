"""
config.py – Design system y configuración del Dashboard de Mortalidad Argentina.
DEIS 2005-2023 · Ministerio de Salud de la Nación Argentina.

Paleta: Institutional Navy · Pearl · Vermillion
Estética: Data journalism de élite (NYT / The Economist aesthetic)
"""

import streamlit as st
import plotly.express as px

# ─────────────────────────────────────────────
# PALETA DE COLORES – SISTEMA DE DISEÑO
# ─────────────────────────────────────────────
COLORS = {
    # Primarios
    "navy":        "#0D2137",   # Azul institucional profundo
    "navy_mid":    "#163554",   # Azul medio sidebar
    "cobalt":      "#1A6FA8",   # Azul acción / gráficos
    "cobalt_light":"#4A9FD4",   # Azul claro / hover
    # Acento
    "vermillion":  "#C0392B",   # Rojo alertas / KPI negativo
    "amber":       "#D4820A",   # Ámbar / KPI advertencia
    "emerald":     "#1A6B45",   # Verde KPI positivo
    # Neutros
    "pearl":       "#F7F4EF",   # Fondo cálido (no frío)
    "warm_gray":   "#E8E4DC",   # Bordes y divisores
    "stone":       "#8B8680",   # Texto secundario
    "ink":         "#1A1614",   # Texto principal
    # Sidebar
    "sidebar_text":"#B8CDD8",   # Texto labels sidebar
    "sidebar_sep": "#254460",   # Separador sidebar
}

# ─────────────────────────────────────────────
# SECUENCIAS DE COLOR PARA GRÁFICOS
# ─────────────────────────────────────────────
COLOR_SEQ = [
    "#1A6FA8", "#D4820A", "#1A6B45", "#7B3F9E",
    "#C0392B", "#2E8B8B", "#B8860B", "#4A6FA8",
]
COLOR_SEQ_COMPARE = ["#1A6FA8", "#D4820A"]  # Azul · Ámbar

# Escala continua: Pearl → Navy
COLOR_SCALE_NAVY = ["#EAF2F8", "#A9CCE3", "#5DADE2", "#2980B9", "#1A5276", "#0D2137"]
# Escala divergente para brechas
COLOR_SCALE_DIV  = ["#1A6FA8", "#EAF2F8", "#D4820A"]

PLOTLY_TEMPLATE = "plotly_white"

# Alias de compatibilidad
COMPARE_COLORS = COLOR_SEQ_COMPARE
primary = COLORS["navy"]
secondary = COLORS["cobalt"]


# ─────────────────────────────────────────────
# CSS PREMIUM
# ─────────────────────────────────────────────
def inject_custom_css() -> None:
    """Inyecta el sistema de diseño editorial mediante CSS."""
    st.markdown(
        f"""
        <style>
        /* ═══════════════════════════════════════════
           GOOGLE FONTS – TIPOGRAFÍA EDITORIAL
        ═══════════════════════════════════════════ */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

        /* ═══════════════════════════════════════════
           BODY & FONDO
        ═══════════════════════════════════════════ */
        .stApp {{
            background-color: {COLORS['pearl']};
            font-family: 'Source Sans 3', sans-serif;
        }}

        /* ═══════════════════════════════════════════
           SIDEBAR PREMIUM
        ═══════════════════════════════════════════ */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['navy']} 0%, {COLORS['navy_mid']} 100%);
            border-right: 1px solid {COLORS['sidebar_sep']};
        }}
        [data-testid="stSidebar"] * {{
            font-family: 'Source Sans 3', sans-serif !important;
        }}
        [data-testid="stSidebar"] .stMarkdown p {{
            color: {COLORS['sidebar_text']};
            font-size: 0.82rem;
        }}
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stSlider label,
        [data-testid="stSidebar"] .stRadio label {{
            color: {COLORS['sidebar_text']} !important;
            font-weight: 600 !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }}
        [data-testid="stSidebar"] .stRadio > div > label > div > p {{
            color: #CDDBE5 !important;
            font-size: 0.88rem !important;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: {COLORS['sidebar_sep']} !important;
            margin: 14px 0 !important;
        }}
        /* Logo / Título sidebar */
        .sidebar-logo {{
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
            font-weight: 900;
            color: #FFFFFF;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }}
        .sidebar-subtitle {{
            font-size: 0.72rem;
            color: {COLORS['sidebar_text']};
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-top: 2px;
        }}
        .sidebar-badge {{
            display: inline-block;
            background: {COLORS['cobalt']};
            color: white;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 2px;
            margin-top: 6px;
        }}

        /* ═══════════════════════════════════════════
           ENCABEZADO PRINCIPAL
        ═══════════════════════════════════════════ */
        .main-header {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.6rem, 3vw, 2.4rem);
            font-weight: 900;
            color: {COLORS['navy']};
            letter-spacing: -0.03em;
            line-height: 1.1;
            margin: 0;
        }}
        .main-subheader {{
            font-size: 0.82rem;
            color: {COLORS['stone']};
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-top: 6px;
            font-weight: 600;
        }}
        .header-rule {{
            height: 3px;
            background: linear-gradient(90deg, {COLORS['navy']} 0%, {COLORS['cobalt']} 50%, transparent 100%);
            border: none;
            margin: 12px 0 20px 0;
        }}

        /* ═══════════════════════════════════════════
           KPI CARDS
        ═══════════════════════════════════════════ */
        .kpi-card {{
            background: {COLORS['navy']};
            border-radius: 6px;
            padding: 22px 20px 18px;
            color: white;
            text-align: left;
            box-shadow: 0 2px 12px rgba(13,33,55,0.18);
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border-top: 3px solid {COLORS['cobalt']};
        }}
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: -30px; right: -30px;
            width: 80px; height: 80px;
            border-radius: 50%;
            background: rgba(255,255,255,0.04);
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(13,33,55,0.25);
        }}
        .kpi-value {{
            font-family: 'Playfair Display', serif;
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.02em;
            margin-bottom: 6px;
        }}
        .kpi-label {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.75;
            font-weight: 600;
        }}
        .kpi-sub {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            opacity: 0.6;
            margin-top: 4px;
        }}
        .kpi-card-green {{
            background: {COLORS['emerald']};
            border-top-color: #27AE60;
        }}
        .kpi-card-accent {{
            background: {COLORS['vermillion']};
            border-top-color: #E74C3C;
        }}
        .kpi-card-amber {{
            background: #7D4E0A;
            border-top-color: {COLORS['amber']};
        }}
        .kpi-card-orange {{
            background: #7A3D05;
            border-top-color: {COLORS['amber']};
        }}

        /* ═══════════════════════════════════════════
           SECTION HEADERS
        ═══════════════════════════════════════════ */
        .section-header {{
            font-family: 'Playfair Display', serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: {COLORS['navy']};
            letter-spacing: -0.01em;
            margin: 32px 0 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid {COLORS['warm_gray']};
            position: relative;
        }}
        .section-header::after {{
            content: '';
            position: absolute;
            bottom: -2px; left: 0;
            width: 48px; height: 2px;
            background: {COLORS['cobalt']};
        }}
        .section-header-compare {{
            font-family: 'Playfair Display', serif;
            font-size: 1.05rem;
            font-weight: 700;
            color: {COLORS['navy']};
            margin: 28px 0 14px;
            padding: 10px 14px;
            background: white;
            border-left: 4px solid {COLORS['amber']};
            border-radius: 0 4px 4px 0;
            box-shadow: 0 1px 4px rgba(13,33,55,0.08);
        }}

        /* ═══════════════════════════════════════════
           BLOQUE IA – INSIGHT PREMIUM
        ═══════════════════════════════════════════ */
        .ai-block {{
            background: white;
            border-left: 4px solid {COLORS['cobalt']};
            border-radius: 0 6px 6px 0;
            padding: 14px 18px;
            margin-top: 8px;
            font-size: 0.88rem;
            color: {COLORS['ink']};
            line-height: 1.65;
            box-shadow: 0 1px 6px rgba(13,33,55,0.07);
        }}
        .ai-block strong {{
            color: {COLORS['navy']};
            font-weight: 700;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .ai-block-compare {{
            background: #FFFBF5;
            border-left: 4px solid {COLORS['amber']};
            border-radius: 0 6px 6px 0;
            padding: 14px 18px;
            margin-top: 8px;
            font-size: 0.88rem;
            color: {COLORS['ink']};
            line-height: 1.65;
            box-shadow: 0 1px 6px rgba(180,100,0,0.07);
        }}
        .ai-block-compare strong {{
            color: #7D4E0A;
            font-weight: 700;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        /* ═══════════════════════════════════════════
           INFO BOX (NOTA METODOLÓGICA)
        ═══════════════════════════════════════════ */
        .info-box {{
            background: white;
            border: 1px solid {COLORS['warm_gray']};
            border-top: 3px solid {COLORS['cobalt_light']};
            border-radius: 4px;
            padding: 14px 18px;
            font-size: 0.82rem;
            color: {COLORS['stone']};
            line-height: 1.6;
        }}
        .info-box strong {{
            color: {COLORS['navy']};
        }}
        .info-box code {{
            background: {COLORS['warm_gray']};
            padding: 1px 5px;
            border-radius: 3px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
        }}

        /* ═══════════════════════════════════════════
           DIVISOR
        ═══════════════════════════════════════════ */
        .custom-divider {{
            border: none;
            border-top: 1px solid {COLORS['warm_gray']};
            margin: 28px 0;
        }}

        /* ═══════════════════════════════════════════
           CHIP DE PROVINCIA (COMPARATIVO)
        ═══════════════════════════════════════════ */
        .prov-chip-a {{
            background: rgba(26,111,168,0.25);
            color: #8EC8E8;
            padding: 2px 8px;
            border-radius: 2px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}
        .prov-chip-b {{
            background: rgba(212,130,10,0.25);
            color: #F0B84A;
            padding: 2px 8px;
            border-radius: 2px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        /* ═══════════════════════════════════════════
           DELTA INDICATORS
        ═══════════════════════════════════════════ */
        .delta-up   {{ color: #E07B78; font-size: 0.72rem; font-weight: 700; }}
        .delta-down {{ color: #7BC8A4; font-size: 0.72rem; font-weight: 700; }}
        .delta-neu  {{ color: #A8A8A8; font-size: 0.72rem; }}

        /* ═══════════════════════════════════════════
           TABS REFINADOS
        ═══════════════════════════════════════════ */
        .stTabs [data-baseweb="tab-list"] {{
            background: transparent;
            gap: 0;
            border-bottom: 2px solid {COLORS['warm_gray']};
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Source Sans 3', sans-serif;
            font-weight: 600;
            font-size: 0.88rem;
            letter-spacing: 0.03em;
            color: {COLORS['stone']};
            padding: 10px 22px;
            border-radius: 0;
            transition: color 0.2s;
        }}
        .stTabs [aria-selected="true"] {{
            color: {COLORS['navy']} !important;
            border-bottom: 2px solid {COLORS['navy']} !important;
            background: transparent !important;
        }}

        /* ═══════════════════════════════════════════
           BOTÓN DE DESCARGA
        ═══════════════════════════════════════════ */
        .stDownloadButton > button {{
            background: {COLORS['navy']};
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.82rem;
            letter-spacing: 0.04em;
            padding: 8px 18px;
            transition: background 0.2s;
        }}
        .stDownloadButton > button:hover {{
            background: {COLORS['cobalt']};
        }}

        /* ═══════════════════════════════════════════
           EXPANDER
        ═══════════════════════════════════════════ */
        .streamlit-expanderHeader {{
            font-weight: 600;
            font-size: 0.88rem;
            color: {COLORS['navy']};
        }}

        /* ═══════════════════════════════════════════
           SCROLLBAR CUSTOM
        ═══════════════════════════════════════════ */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: {COLORS['warm_gray']}; }}
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['cobalt_light']};
            border-radius: 3px;
        }}

        /* ═══════════════════════════════════════════
           ANIMACIÓN FADE-IN PARA SECCIONES
        ═══════════════════════════════════════════ */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        .section-header, .kpi-card, .ai-block, .ai-block-compare {{
            animation: fadeInUp 0.35s ease both;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def setup_config() -> None:
    """Configuración inicial de la página."""
    st.set_page_config(
        page_title="DEIS · Mortalidad Argentina",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://www.argentina.gob.ar/salud/deis",
            "About": "Dashboard de Mortalidad · DEIS 2005–2023 · Ministerio de Salud de la Nación Argentina",
        },
    )
    inject_custom_css()
