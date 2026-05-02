"""
config.py – Configuración general, constantes de diseño y estilos CSS.
Dashboard de Mortalidad en Argentina - DEIS 2005-2023
"""

import streamlit as st
import plotly.express as px


# ─────────────────────────────────────────────
# CONSTANTES DE DISEÑO
# ─────────────────────────────────────────────
COLORS = {
    "primary":   "#1B4F72",
    "secondary": "#2E86C1",
    "accent":    "#E74C3C",
    "neutral":   "#ECF0F1",
    "text_dark": "#1C2833",
    "success":   "#1E8449",
    "warn":      "#D4AC0D",
}

PLOTLY_TEMPLATE = "plotly_white"
COLOR_SEQ = px.colors.qualitative.Set2


# ─────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────
def inject_custom_css() -> None:
    """Inyecta el bloque CSS personalizado en la aplicación Streamlit."""
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# INICIALIZACIÓN GENERAL
# ─────────────────────────────────────────────
def setup_config() -> None:
    """
    Agrupa toda la inicialización de configuración de la app:
    - Configuración de página de Streamlit.
    - Inyección del CSS personalizado.

    Debe llamarse como la primera instrucción de app.py, antes de cualquier
    otro componente de Streamlit.
    """
    st.set_page_config(
        page_title="DEIS | Mortalidad Argentina",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()
