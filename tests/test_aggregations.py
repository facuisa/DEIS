import pandas as pd

from src.analysis.aggregations import (
    comparison_cause_gap,
    comparison_distribution,
    comparison_table_parts,
    comparison_time_series,
    comparison_top_causes,
    comparison_treemap_data,
    distribution_by,
    filtered_table_aggregate,
    subgroup_distribution,
    territorial_heatmap_data,
    territorial_ranking,
    time_series_by,
    time_series_by_sex,
    time_series_total,
    top_causes,
)


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "anio": 2020,
                "provincia": "A",
                "region": "R1",
                "sexo_desc": "Mujer",
                "EDAD_norm": "65+",
                "CAUSA_grupo_macro": "Cardio",
                "causa_desc": "Infarto",
                "subgrupo": "S1",
                "CUENTA": 10,
                "valor_metrica": 10.0,
            },
            {
                "anio": 2020,
                "provincia": "A",
                "region": "R1",
                "sexo_desc": "Varón",
                "EDAD_norm": "35-64",
                "CAUSA_grupo_macro": "Tumores",
                "causa_desc": "Pulmón",
                "subgrupo": "S2",
                "CUENTA": 20,
                "valor_metrica": 20.0,
            },
            {
                "anio": 2021,
                "provincia": "B",
                "region": "R2",
                "sexo_desc": "Mujer",
                "EDAD_norm": "65+",
                "CAUSA_grupo_macro": "Cardio",
                "causa_desc": "Infarto",
                "subgrupo": "S1",
                "CUENTA": 5,
                "valor_metrica": 5.0,
            },
        ]
    )


def test_basic_aggregations_return_expected_frames() -> None:
    df = _df()

    assert top_causes(df, 1).iloc[0]["causa_desc"] == "Pulmón"
    assert distribution_by(df, "sexo_desc").set_index("sexo_desc")["valor_metrica"].to_dict() == {
        "Mujer": 15.0,
        "Varón": 20.0,
    }
    assert territorial_ranking(df, "provincia")["provincia"].tolist() == ["B", "A"]
    assert time_series_total(df).set_index("anio")["valor_metrica"].to_dict() == {
        2020: 30.0,
        2021: 5.0,
    }
    assert time_series_by_sex(df).shape[0] == 3


def test_territorial_subgroup_time_series_and_table_aggregations() -> None:
    df = _df()

    pivot_src, pivot, pivot_resumen = territorial_heatmap_data(df, "provincia")
    assert set(pivot_src.columns) == {"provincia", "CAUSA_grupo_macro", "valor_metrica"}
    assert pivot.loc["A", "Cardio"] == 10.0
    assert pivot_resumen.iloc[0]["valor_metrica"] == 20.0

    assert subgroup_distribution(df, "subgrupo").set_index("subgrupo")["valor_metrica"].to_dict() == {
        "S1": 15.0,
        "S2": 20.0,
    }
    assert set(time_series_by(df, "CAUSA_grupo_macro", 1)["CAUSA_grupo_macro"]) == {"Tumores"}

    table = filtered_table_aggregate(df, ["anio", "provincia", "causa_desc"])
    assert table.iloc[0]["valor_metrica"] == 20.0


def test_comparison_aggregations_return_expected_shapes_and_values() -> None:
    df_a = _df().query("provincia == 'A'").copy()
    df_b = _df().query("provincia == 'B'").copy()

    assert comparison_time_series(df_a, df_b, "A", "B")["provincia"].tolist() == ["A", "B"]

    top_a = comparison_top_causes(df_a, "A", 2)
    top_b = comparison_top_causes(df_b, "B", 2)
    gap = comparison_cause_gap(top_a, top_b, "A", "B")
    assert gap.iloc[0]["causa_desc"] == "Infarto"
    assert gap.iloc[0]["brecha"] == -5.0

    sex_comp = comparison_distribution(df_a, df_b, "sexo_desc", "A", "B")
    assert set(sex_comp["provincia"]) == {"A", "B"}

    tree = comparison_treemap_data(df_a, df_b, "A", "B")
    assert set(tree["provincia"]) == {"A", "B"}

    tbl_a, tbl_b = comparison_table_parts(
        df_a, df_b, ["anio", "CAUSA_grupo_macro", "causa_desc"], "Defunciones", "A", "B"
    )
    assert "Defunciones_A" in tbl_a.columns
    assert "Defunciones_B" in tbl_b.columns
