"""
data_processing.py – Carga, transformación, filtrado y cálculo de métricas.
Dashboard de Mortalidad en Argentina - DEIS 2005-2023
"""

import pandas as pd
import streamlit as st

from src.domain.filters import apply_filters, apply_filters_provincia
from src.domain.metrics import calcular_metrica, calcular_metrica_provincia


# Columnas del dataset principal que tienen muchos valores repetidos y se
# usan como dimensiones/códigos/descripciones en filtros, tablas y gráficos.
_CATEGORY_COLUMNS = [
    "CAUSA",
    "MAT",
    "GRUPEDAD",
    "source_file",
    "provincia",
    "sexo_desc",
    "MAT_desc",
    "CAUSA_norm",
    "codigo_causa",
    "causa_desc",
    "EDAD_norm",
    "CAUSA_prefijo",
    "CAUSA_grupo_macro",
    "CAUSA_externa_subgrupo",
    "CAUSA_cardio_subgrupo",
    "CAUSA_tumor_subgrupo",
    "CAUSA_respiratoria_subgrupo",
    "CAUSA_digestiva_subgrupo",
    "CAUSA_infecciosa_subgrupo",
    "CAUSA_endocrina_subgrupo",
    "CAUSA_neuro_subgrupo",
    "CAUSA_genitourinaria_subgrupo",
    "CAUSA_D_subgrupo",
    "CAUSA_R_subgrupo",
    "CAUSA_P_subgrupo",
    "CAUSA_Q_subgrupo",
    "CAUSA_F_subgrupo",
    "region",
    "grupo_etario_estudio",
]

_NUMERIC_DOWNCAST_COLUMNS = [
    "PROVRES",
    "SEXO",
    "CUENTA",
    "anio",
    "PROVRES_norm",
    "codigo",
    "SEXO_norm",
    "codigo_sexo",
    "EDAD_orden",
]


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce memoria del dataset sin cambiar valores ni columnas.

    - Convierte dimensiones textuales repetitivas a ``category``.
    - Reduce enteros a subtipos más chicos con ``downcast="integer"``.

    Devuelve una copia optimizada para no mutar el DataFrame recibido.
    """
    optimized = df.copy()

    for col in _CATEGORY_COLUMNS:
        if col in optimized.columns and optimized[col].dtype == "object":
            optimized[col] = optimized[col].astype("category")

    for col in _NUMERIC_DOWNCAST_COLUMNS:
        if col in optimized.columns:
            optimized[col] = pd.to_numeric(optimized[col], downcast="integer")

    return optimized


# ─────────────────────────────────────────────
# ANÁLISIS AUTOMÁTICO POR IA (con caché)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def obtener_analisis_ia(datos_df: pd.DataFrame, titulo_grafico: str) -> str:
    """
    Envía un resumen tabulado de los datos a Groq/Llama-3.3 y devuelve
    una interpretación epidemiológica breve (≤ 3 líneas).
    Resultado cacheado: no se repite si los datos no cambian.
    """
    from groq import Groq

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    resumen_texto = datos_df.to_string(index=False)

    prompt = f"""Sos un experto en estadísticas de salud pública de Argentina.
Analizá estos datos del gráfico "{titulo_grafico}":

{resumen_texto}

REGLAS ESTRICTAS:
- Basate ÚNICAMENTE en los números de la tabla. No inventes contexto externo.
- Si no hay datos suficientes, decí exactamente: "No hay datos suficientes para este análisis."
- Máximo 3 oraciones. Sin bullet points. Sin títulos.
- Mencioná las cifras más relevantes con su valor exacto."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Análisis no disponible: {e}"


@st.cache_data(show_spinner=False)
def obtener_analisis_comparativo_ia(
    datos_a: pd.DataFrame,
    datos_b: pd.DataFrame,
    prov_a: str,
    prov_b: str,
    nombre_metrica: str,
    contexto: str = "",
) -> str:
    """
    Análisis comparativo especializado entre dos provincias.
    Recibe los datos de cada provincia por separado para que el modelo
    pueda razonar sobre las diferencias explícitamente.
    """
    from groq import Groq

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    resumen_a = datos_a.to_string(index=False)
    resumen_b = datos_b.to_string(index=False)

    prompt = f"""Sos un epidemiólogo argentino experto en análisis de mortalidad provincial.
Comparás los datos de {prov_a} vs {prov_b} — métrica: {nombre_metrica}.
{('Contexto adicional: ' + contexto) if contexto else ''}

=== {prov_a} ===
{resumen_a}

=== {prov_b} ===
{resumen_b}

REGLAS ESTRICTAS:
- Basate ÚNICAMENTE en los números de las tablas. No inventes contexto externo.
- Identificá la diferencia más llamativa entre ambas provincias con sus valores exactos.
- Si hay una brecha notable, mencionala con su magnitud.
- Máximo 4 oraciones. Sin bullet points."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=280,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Análisis comparativo no disponible: {e}"


# ─────────────────────────────────────────────
# CARGA Y CACHÉ DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando dataset DEIS…")
def load_data() -> pd.DataFrame:
    """Carga el parquet principal de mortalidad y normaliza tipos."""
    df = pd.read_parquet("data/mortalidad_analizada_2005_2023.parquet")
    df.columns = df.columns.str.strip()
    df["CUENTA"] = pd.to_numeric(df["CUENTA"], errors="coerce").fillna(0).astype(int)
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    return optimize_dtypes(df)


@st.cache_data(show_spinner="Cargando población INDEC…")
def load_poblacion() -> pd.DataFrame:
    """
    Carga proyecciones de población INDEC 2010-2023.

    Columnas esperadas: provincia, anio, poblacion_total,
    poblacion_varones, poblacion_mujeres, provincia_pdf, pagina_pdf.
    """
    pop = pd.read_parquet(
        "data/poblacion_indec_provincias_2010_2023_normalizada.parquet"
    )
    pop.columns = pop.columns.str.strip()
    pop["anio"] = pd.to_numeric(pop["anio"], errors="coerce")
    for col in ("poblacion_total", "poblacion_varones", "poblacion_mujeres"):
        if col in pop.columns:
            pop[col] = pd.to_numeric(pop[col], errors="coerce")
    return pop


# ─────────────────────────────────────────────
# DETECCIÓN DE SUBGRUPOS
# ─────────────────────────────────────────────
def get_subgroup_columns(df: pd.DataFrame) -> list[str]:
    """Detecta columnas que representan subgrupos de causa."""
    keywords = ["subgrupo", "subtipo", "sub_", "grupo_", "_sub"]
    return [c for c in df.columns if any(k in c.lower() for k in keywords)]
