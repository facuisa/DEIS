"""
data_processing.py – Carga, transformación, filtrado y cálculo de métricas.
Dashboard de Mortalidad en Argentina - DEIS 2005-2023
"""

import pandas as pd
import streamlit as st


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


# ─────────────────────────────────────────────
# APLICAR FILTROS GLOBALES
# ─────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica los filtros globales del sidebar al DataFrame.
    Trabaja sobre una copia; el original nunca se modifica.
    """
    fdf = df.copy()
    fdf = fdf[fdf["anio"].between(filters["anio"][0], filters["anio"][1])]

    if filters["region"] and "Todas" not in filters["region"]:
        fdf = fdf[fdf["region"].isin(filters["region"])]

    if filters["provincia"] and "Todas" not in filters["provincia"]:
        fdf = fdf[fdf["provincia"].isin(filters["provincia"])]

    if filters["sexo"] and "Todos" not in filters["sexo"]:
        fdf = fdf[fdf["sexo_desc"].isin(filters["sexo"])]

    if filters["edad"] and "Todos" not in filters["edad"]:
        fdf = fdf[fdf["EDAD_norm"].isin(filters["edad"])]

    if filters["causa_macro"] and "Todas" not in filters["causa_macro"]:
        fdf = fdf[fdf["CAUSA_grupo_macro"].isin(filters["causa_macro"])]

    return fdf


def apply_filters_provincia(
    df: pd.DataFrame, filters: dict, provincia: str
) -> pd.DataFrame:
    """
    Versión del filtro para el módulo comparativo:
    aplica todos los filtros globales EXCEPTO provincia/región,
    y fuerza la provincia al valor indicado.
    Esto permite que los filtros de año, sexo, edad y causa macro
    del sidebar afecten también al comparativo.
    """
    fdf = df.copy()
    fdf = fdf[fdf["anio"].between(filters["anio"][0], filters["anio"][1])]
    fdf = fdf[fdf["provincia"] == provincia]

    if filters["sexo"] and "Todos" not in filters["sexo"]:
        fdf = fdf[fdf["sexo_desc"].isin(filters["sexo"])]

    if filters["edad"] and "Todos" not in filters["edad"]:
        fdf = fdf[fdf["EDAD_norm"].isin(filters["edad"])]

    # En el comparativo la causa macro se controla en el módulo,
    # no desde el filtro global, para no restringir demasiado.

    return fdf


# ─────────────────────────────────────────────
# CÁLCULO DE MÉTRICA
# ─────────────────────────────────────────────
def _col_poblacion(filters: dict, advertencias: list[str]) -> str:
    """Determina qué columna de población usar según el filtro de sexo activo."""
    sexo_filtro = filters.get("sexo", ["Todos"])
    sexo_activo = bool(sexo_filtro) and "Todos" not in sexo_filtro

    if not sexo_activo:
        return "poblacion_total"

    sexos_norm = {s.lower().strip() for s in sexo_filtro}
    varones = {"varón", "varon", "masculino", "masc", "m"}
    mujeres = {"mujer", "femenino", "fem", "f"}

    if sexos_norm <= varones:
        return "poblacion_varones"
    elif sexos_norm <= mujeres:
        return "poblacion_mujeres"
    else:
        advertencias.append(
            "⚠️ Varios sexos seleccionados simultáneamente: se usa **población total** "
            "para el cálculo de tasa. Interpretá los resultados con cautela."
        )
        return "poblacion_total"


def calcular_metrica(
    df_filtrado: pd.DataFrame,
    df_poblacion: pd.DataFrame,
    filters: dict,
    metrica: str,
) -> tuple[pd.DataFrame, str, str, list[str]]:
    """
    Agrega ``valor_metrica`` al DataFrame filtrado según la métrica elegida.
    No modifica df_filtrado ni df_poblacion.

    Returns
    -------
    (df, nombre_metrica, formato_plotly, advertencias)
    """
    advertencias: list[str] = []
    df = df_filtrado.copy()

    if metrica == "Defunciones absolutas":
        df["valor_metrica"] = df["CUENTA"]
        return df, "Defunciones", ":,.0f", advertencias

    # ── Tasa c/100k ───────────────────────────────────────────────────────────
    anio_min = int(filters["anio"][0])
    anio_max = int(filters["anio"][1])

    if anio_min < 2010:
        advertencias.append(
            f"⚠️ Población INDEC disponible desde 2010. "
            f"Los años {anio_min}–{min(anio_max, 2009)} se muestran como valores absolutos."
        )
        df_tasa = df[df["anio"] >= 2010].copy()
        df_abs  = df[df["anio"] < 2010].copy()
        df_abs["valor_metrica"] = df_abs["CUENTA"]
    else:
        df_tasa = df.copy()
        df_abs  = pd.DataFrame()

    if df_tasa.empty:
        df["valor_metrica"] = df["CUENTA"]
        return df, "Defunciones", ":,.0f", advertencias

    col_pob = _col_poblacion(filters, advertencias)

    if col_pob not in df_poblacion.columns:
        advertencias.append(
            f"⚠️ Columna '{col_pob}' no encontrada en INDEC. Se usan valores absolutos."
        )
        df["valor_metrica"] = df["CUENTA"]
        return df, "Defunciones", ":,.0f", advertencias

    pop_merge = (
        df_poblacion[["provincia", "anio", col_pob]]
        .dropna(subset=["provincia", "anio", col_pob])
        .drop_duplicates(subset=["provincia", "anio"])
    )

    try:
        df_tasa = df_tasa.merge(
            pop_merge.rename(columns={col_pob: "_pob_"}),
            on=["provincia", "anio"],
            how="left",
            validate="m:1",
        )
    except pd.errors.MergeError as e:
        advertencias.append(f"⚠️ Error en merge con población: {e}. Se usan absolutos.")
        df["valor_metrica"] = df["CUENTA"]
        return df, "Defunciones", ":,.0f", advertencias

    sin_match = (
        df_tasa.loc[df_tasa["_pob_"].isna(), "provincia"].dropna().unique().tolist()
    )
    if sin_match:
        advertencias.append(
            f"⚠️ Sin datos de población INDEC para: **{', '.join(sorted(sin_match))}**. "
            "Esas filas se excluyen del cálculo de tasa."
        )
        df_tasa = df_tasa[df_tasa["_pob_"].notna()].copy()

    if df_tasa.empty:
        df["valor_metrica"] = df["CUENTA"]
        return df, "Defunciones", ":,.0f", advertencias

    df_tasa["valor_metrica"] = (df_tasa["CUENTA"] / df_tasa["_pob_"]) * 100_000
    df_tasa = df_tasa.drop(columns=["_pob_"])

    resultado = (
        pd.concat([df_tasa, df_abs], ignore_index=True)
        if not df_abs.empty
        else df_tasa
    )
    return resultado, "Tasa c/100k", ":.2f", advertencias


def calcular_metrica_provincia(
    df_raw: pd.DataFrame,
    df_poblacion: pd.DataFrame,
    filters: dict,
    metrica: str,
    provincia: str,
) -> tuple[pd.DataFrame, str, str, list[str]]:
    """
    Versión de calcular_metrica para una provincia específica.
    Usa apply_filters_provincia internamente.
    Pensada para el módulo comparativo.
    """
    df_prov = apply_filters_provincia(df_raw, filters, provincia)
    # Creamos un filters temporal con la provincia forzada para que
    # _col_poblacion funcione igual
    filters_tmp = {**filters, "provincia": [provincia], "region": ["Todas"]}
    return calcular_metrica(df_prov, df_poblacion, filters_tmp, metrica)
