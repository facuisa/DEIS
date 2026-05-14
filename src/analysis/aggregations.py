"""Agregaciones puras usadas por la capa de renderizado Streamlit."""

import pandas as pd


def top_causes(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Devuelve las principales causas por valor de métrica."""
    return (
        df.groupby("causa_desc", observed=True)["valor_metrica"]
        .sum()
        .nlargest(n)
        .reset_index()
        .sort_values("valor_metrica")
    )


def distribution_by(df: pd.DataFrame, column: str, sort_desc: bool = False) -> pd.DataFrame:
    """Agrega valor_metrica por una dimensión categórica."""
    out = df.groupby(column, observed=True)["valor_metrica"].sum().reset_index()
    if sort_desc:
        out = out.sort_values("valor_metrica", ascending=False)
    return out


def metric_by_province_year(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega valor_metrica por provincia y año."""
    return df.groupby(["provincia", "anio"], observed=True)["valor_metrica"].sum().reset_index()


def territorial_ranking(df: pd.DataFrame, geo_column: str) -> pd.DataFrame:
    """Ranking territorial ascendente por valor de métrica."""
    return (
        df.groupby(geo_column, observed=True)["valor_metrica"]
        .sum()
        .reset_index()
        .sort_values("valor_metrica", ascending=True)
    )


def territorial_heatmap_data(
    df: pd.DataFrame, geo_column: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Agrega datos para heatmap territorial y resumen de IA."""
    pivot_src = (
        df.groupby([geo_column, "CAUSA_grupo_macro"], observed=True)["valor_metrica"]
        .sum()
        .reset_index()
    )
    pivot = (
        pivot_src
        .pivot(index=geo_column, columns="CAUSA_grupo_macro", values="valor_metrica")
        .fillna(0)
    )
    pivot_resumen = (
        pivot_src[pivot_src["valor_metrica"] > 0]
        .sort_values("valor_metrica", ascending=False)
        .head(30)
    )
    return pivot_src, pivot, pivot_resumen


def subgroup_distribution(df: pd.DataFrame, subgroup_column: str) -> pd.DataFrame:
    """Agrega métrica por columna de subgrupo, excluyendo nulos y vacíos."""
    return (
        df.groupby(subgroup_column, observed=True)["valor_metrica"]
        .sum()
        .reset_index()
        .dropna(subset=[subgroup_column])
        .query(f"`{subgroup_column}` != ''")
        .sort_values("valor_metrica", ascending=True)
    )


def time_series_total(df: pd.DataFrame) -> pd.DataFrame:
    """Serie temporal anual sin desglose."""
    return df.groupby("anio", observed=True)["valor_metrica"].sum().reset_index()


def time_series_by(df: pd.DataFrame, column: str, max_categories: int) -> pd.DataFrame:
    """Serie temporal anual por las categorías principales de una dimensión."""
    top_cats = (
        df.groupby(column, observed=True)["valor_metrica"]
        .sum()
        .nlargest(max_categories)
        .index
        .tolist()
    )
    return (
        df[df[column].isin(top_cats)]
        .groupby(["anio", column], observed=True)["valor_metrica"]
        .sum()
        .reset_index()
    )


def time_series_by_sex(df: pd.DataFrame) -> pd.DataFrame:
    """Serie temporal anual por sexo."""
    return df.groupby(["anio", "sexo_desc"], observed=True)["valor_metrica"].sum().reset_index()


def filtered_table_aggregate(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Vista agregada para la tabla filtrada."""
    return (
        df.groupby(group_cols, observed=True)[["CUENTA", "valor_metrica"]]
        .sum()
        .reset_index()
        .sort_values(["anio", "valor_metrica"], ascending=[True, False])
    )


def comparison_time_series(
    df_a: pd.DataFrame, df_b: pd.DataFrame, prov_a: str, prov_b: str
) -> pd.DataFrame:
    """Serie temporal comparativa entre dos provincias."""
    ts_a = time_series_total(df_a).assign(provincia=prov_a)
    ts_b = time_series_total(df_b).assign(provincia=prov_b)
    return pd.concat([ts_a, ts_b], ignore_index=True)


def comparison_top_causes(
    df: pd.DataFrame, provincia: str, n: int
) -> pd.DataFrame:
    """Top de causas para una provincia en formato comparativo."""
    return (
        df.groupby("causa_desc", observed=True)["valor_metrica"]
        .sum()
        .nlargest(n)
        .reset_index()
        .assign(provincia=provincia)
    )


def comparison_cause_gap(
    top_a: pd.DataFrame, top_b: pd.DataFrame, prov_a: str, prov_b: str
) -> pd.DataFrame:
    """Brecha de métrica entre provincias para causas presentes en ambos tops."""
    causas_comunes = set(top_a["causa_desc"]) & set(top_b["causa_desc"])
    if not causas_comunes:
        return pd.DataFrame(columns=["causa_desc", prov_a, prov_b, "brecha"])

    m_a = top_a[top_a["causa_desc"].isin(causas_comunes)][
        ["causa_desc", "valor_metrica"]
    ].rename(columns={"valor_metrica": prov_a})
    m_b = top_b[top_b["causa_desc"].isin(causas_comunes)][
        ["causa_desc", "valor_metrica"]
    ].rename(columns={"valor_metrica": prov_b})
    out = m_a.merge(m_b, on="causa_desc")
    out["brecha"] = out[prov_b] - out[prov_a]
    return out.sort_values("brecha")


def comparison_distribution(
    df_a: pd.DataFrame, df_b: pd.DataFrame, column: str, prov_a: str, prov_b: str
) -> pd.DataFrame:
    """Distribución comparativa por una dimensión."""
    dist_a = distribution_by(df_a, column).assign(provincia=prov_a)
    dist_b = distribution_by(df_b, column).assign(provincia=prov_b)
    return pd.concat([dist_a, dist_b], ignore_index=True)


def comparison_treemap_data(
    df_a: pd.DataFrame, df_b: pd.DataFrame, prov_a: str, prov_b: str
) -> pd.DataFrame:
    """Datos agregados para treemap comparativo."""
    group_cols = ["CAUSA_grupo_macro", "causa_desc"]
    tree_a = df_a.groupby(group_cols, observed=True)["valor_metrica"].sum().reset_index().assign(provincia=prov_a)
    tree_b = df_b.groupby(group_cols, observed=True)["valor_metrica"].sum().reset_index().assign(provincia=prov_b)
    out = pd.concat([tree_a, tree_b], ignore_index=True)
    return out[out["valor_metrica"] > 0]


def comparison_table_parts(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    group_cols: list[str],
    metric_name: str,
    prov_a: str,
    prov_b: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tablas agregadas por provincia para la tabla comparativa final."""
    tbl_a = (
        df_a.groupby(group_cols, observed=True)["valor_metrica"]
        .sum()
        .reset_index()
        .rename(columns={"valor_metrica": f"{metric_name}_{prov_a}"})
    )
    tbl_b = (
        df_b.groupby(group_cols, observed=True)["valor_metrica"]
        .sum()
        .reset_index()
        .rename(columns={"valor_metrica": f"{metric_name}_{prov_b}"})
    )
    return tbl_a, tbl_b
