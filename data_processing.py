"""
data_processing.py – Carga, transformación y filtrado de datos.
Dashboard de Mortalidad en Argentina - DEIS 2005-2023
"""

import pandas as pd
import streamlit as st


# ─────────────────────────────────────────────
# CARGA Y CACHÉ DE DATOS
# ─────────────────────────────────────────────
# ... (tus otros imports arriba)

# 1. Función de la IA con Caché
@st.cache_data(show_spinner=False)
def obtener_analisis_ia(datos_df, titulo_grafico):
    from groq import Groq
    # No hace falta "import streamlit as st" aquí si ya lo tenés arriba del todo en el archivo
    
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    resumen_texto = datos_df.to_string(index=False)
    
    prompt = f"""
    Actúa como un experto en estadísticas de salud de Argentina.
    Analiza estos datos del gráfico "{titulo_grafico}":
    {resumen_texto}
    
    REGLAS ESTRICTAS:
    - Análisis basado ÚNICAMENTE en estos números.
    - Sé muy breve (máximo 3 líneas).
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Análisis no disponible: {e}"

# 2. Tu función de carga de datos (que ya estaba bien)
@st.cache_data(show_spinner="Cargando dataset DEIS…")
def load_data() -> pd.DataFrame:
    df = pd.read_parquet("data/mortalidad_analizada_2005_2023.parquet")
    df.columns = df.columns.str.strip()
    df["CUENTA"] = pd.to_numeric(df["CUENTA"], errors="coerce").fillna(0).astype(int)
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    return df

# ─────────────────────────────────────────────
# DETECCIÓN DE COLUMNAS DE SUBGRUPOS
# ─────────────────────────────────────────────
def get_subgroup_columns(df: pd.DataFrame) -> list[str]:
    """
    Detecta columnas del DataFrame que parecen representar subgrupos de causa.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame completo cargado desde el dataset.

    Returns
    -------
    list[str]
        Lista de nombres de columnas que contienen palabras clave de subgrupo.
    """
    keywords = ["subgrupo", "subtipo", "sub_", "grupo_", "_sub"]
    return [
        c for c in df.columns
        if any(k in c.lower() for k in keywords)
    ]


# ─────────────────────────────────────────────
# APLICAR FILTROS GLOBALES
# ─────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica los filtros globales seleccionados en el sidebar al DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame completo sin filtrar.
    filters : dict
        Diccionario de filtros con las claves:
        ``anio``, ``region``, ``provincia``, ``sexo``, ``edad``, ``causa_macro``.

    Returns
    -------
    pd.DataFrame
        Subconjunto del DataFrame que cumple con todos los filtros aplicados.
    """
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



def obtener_analisis_ia(datos_df, titulo_grafico):
    """
    Envía un resumen de los datos a la IA y devuelve una descripción.
    """
    from groq import Groq
    # 1. Recuperamos la llave de los secrets de Streamlit
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # 2. Preparamos un resumen muy simple de los datos (solo lo que ve el usuario)
    resumen_texto = datos_df.to_string(index=False)
    
    # 3. El "Prompt" blindado para que no invente nada
    prompt = f"""
    Actúa como un experto en estadísticas de salud de Argentina.
    Analiza estos datos del gráfico "{titulo_grafico}":
    
    {resumen_texto}
    
    REGLAS ESTRICTAS:
    - Tu análisis debe basarse ÚNICAMENTE en estos números.
    - Si no hay datos, di "No hay datos suficientes".
    - No inventes causas externas ni menciones contextos que no estén en la tabla.
    - Sé muy breve (máximo 3 líneas).
    """
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error al generar análisis: {e}"