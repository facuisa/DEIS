"""Cálculo puro de métricas del dashboard DEIS."""

import pandas as pd

from src.domain.filters import apply_filters_provincia


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
        df_abs = df[df["anio"] < 2010].copy()
        df_abs["valor_metrica"] = df_abs["CUENTA"]
    else:
        df_tasa = df.copy()
        df_abs = pd.DataFrame()

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
