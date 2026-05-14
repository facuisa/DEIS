"""Filtros puros del dashboard DEIS."""

import pandas as pd


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
