import pandas as pd
import pytest

from data_processing import apply_filters, calcular_metrica, optimize_dtypes


def _mortalidad_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "anio": 2009,
                "region": "Centro",
                "provincia": "Buenos Aires",
                "sexo_desc": "Mujer",
                "EDAD_norm": "65+",
                "CAUSA_grupo_macro": "Cardio",
                "CUENTA": 7,
            },
            {
                "anio": 2011,
                "region": "Centro",
                "provincia": "Buenos Aires",
                "sexo_desc": "Mujer",
                "EDAD_norm": "65+",
                "CAUSA_grupo_macro": "Cardio",
                "CUENTA": 50,
            },
            {
                "anio": 2012,
                "region": "Centro",
                "provincia": "Córdoba",
                "sexo_desc": "Varón",
                "EDAD_norm": "35-64",
                "CAUSA_grupo_macro": "Tumores",
                "CUENTA": 30,
            },
            {
                "anio": 2013,
                "region": "Cuyo",
                "provincia": "Mendoza",
                "sexo_desc": "Mujer",
                "EDAD_norm": "0-14",
                "CAUSA_grupo_macro": "Externas",
                "CUENTA": 20,
            },
        ]
    )


def _poblacion_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "provincia": "Buenos Aires",
                "anio": 2010,
                "poblacion_total": 100_000,
                "poblacion_varones": 48_000,
                "poblacion_mujeres": 52_000,
            },
            {
                "provincia": "Buenos Aires",
                "anio": 2011,
                "poblacion_total": 100_000,
                "poblacion_varones": 48_000,
                "poblacion_mujeres": 52_000,
            },
            {
                "provincia": "Córdoba",
                "anio": 2012,
                "poblacion_total": 50_000,
                "poblacion_varones": 24_000,
                "poblacion_mujeres": 26_000,
            },
            {
                "provincia": "Mendoza",
                "anio": 2013,
                "poblacion_total": 25_000,
                "poblacion_varones": 12_000,
                "poblacion_mujeres": 13_000,
            },
        ]
    )


def _filters(**overrides: object) -> dict:
    base = {
        "anio": (2009, 2013),
        "region": ["Todas"],
        "provincia": ["Todas"],
        "sexo": ["Todos"],
        "edad": ["Todos"],
        "causa_macro": ["Todas"],
    }
    base.update(overrides)
    return base


def test_apply_filters_filters_by_year_range() -> None:
    result = apply_filters(_mortalidad_df(), _filters(anio=(2011, 2012)))

    assert result["anio"].tolist() == [2011, 2012]


def test_apply_filters_filters_by_province() -> None:
    result = apply_filters(
        _mortalidad_df(),
        _filters(provincia=["Buenos Aires"]),
    )

    assert set(result["provincia"]) == {"Buenos Aires"}
    assert len(result) == 2


def test_apply_filters_filters_by_sex() -> None:
    result = apply_filters(_mortalidad_df(), _filters(sexo=["Mujer"]))

    assert set(result["sexo_desc"]) == {"Mujer"}
    assert len(result) == 3


def test_apply_filters_combines_filters() -> None:
    result = apply_filters(
        _mortalidad_df(),
        _filters(
            anio=(2011, 2013),
            region=["Centro"],
            provincia=["Buenos Aires"],
            sexo=["Mujer"],
            edad=["65+"],
            causa_macro=["Cardio"],
        ),
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["anio"] == 2011
    assert row["provincia"] == "Buenos Aires"
    assert row["sexo_desc"] == "Mujer"
    assert row["CAUSA_grupo_macro"] == "Cardio"


def test_calcular_metrica_absolutos_uses_cuenta_values() -> None:
    df = _mortalidad_df().query("anio >= 2011").copy()

    result, nombre_metrica, fmt, advertencias = calcular_metrica(
        df,
        _poblacion_df(),
        _filters(anio=(2011, 2013)),
        "Defunciones absolutas",
    )

    assert nombre_metrica == "Defunciones"
    assert fmt == ":,.0f"
    assert advertencias == []
    assert result["valor_metrica"].tolist() == result["CUENTA"].tolist()


def test_calcular_metrica_tasa_with_available_population() -> None:
    df = _mortalidad_df().query("anio == 2011 and provincia == 'Buenos Aires'").copy()

    result, nombre_metrica, fmt, advertencias = calcular_metrica(
        df,
        _poblacion_df(),
        _filters(anio=(2011, 2011)),
        "Tasa cada 100.000 habitantes",
    )

    assert nombre_metrica == "Tasa c/100k"
    assert fmt == ":.2f"
    assert advertencias == []
    assert result.iloc[0]["valor_metrica"] == pytest.approx(50.0)


def test_calcular_metrica_tasa_uses_sex_specific_population() -> None:
    df = _mortalidad_df().query("anio == 2011 and provincia == 'Buenos Aires'").copy()

    result, _, _, advertencias = calcular_metrica(
        df,
        _poblacion_df(),
        _filters(anio=(2011, 2011), sexo=["Mujer"]),
        "Tasa cada 100.000 habitantes",
    )

    assert advertencias == []
    assert result.iloc[0]["valor_metrica"] == pytest.approx(50 / 52_000 * 100_000)


def test_calcular_metrica_tasa_excludes_rows_with_missing_population() -> None:
    df = _mortalidad_df().query("anio in [2011, 2012]").copy()
    poblacion_sin_cordoba = _poblacion_df().query("provincia != 'Córdoba'").copy()

    result, nombre_metrica, _, advertencias = calcular_metrica(
        df,
        poblacion_sin_cordoba,
        _filters(anio=(2011, 2012)),
        "Tasa cada 100.000 habitantes",
    )

    assert nombre_metrica == "Tasa c/100k"
    assert set(result["provincia"]) == {"Buenos Aires"}
    assert any("Sin datos de población INDEC" in advertencia for advertencia in advertencias)


def test_calcular_metrica_tasa_keeps_pre_2010_rows_as_absolutes_when_mixed_period() -> None:
    df = _mortalidad_df().query("anio in [2009, 2011]").copy()

    result, nombre_metrica, fmt, advertencias = calcular_metrica(
        df,
        _poblacion_df(),
        _filters(anio=(2009, 2011)),
        "Tasa cada 100.000 habitantes",
    )

    assert nombre_metrica == "Tasa c/100k"
    assert fmt == ":.2f"
    assert any("Población INDEC disponible desde 2010" in advertencia for advertencia in advertencias)

    valores_por_anio = result.set_index("anio")["valor_metrica"].to_dict()
    assert valores_por_anio[2009] == 7
    assert valores_por_anio[2011] == pytest.approx(50.0)


def test_calcular_metrica_tasa_all_pre_2010_falls_back_to_absolutes() -> None:
    df = _mortalidad_df().query("anio == 2009").copy()

    result, nombre_metrica, fmt, advertencias = calcular_metrica(
        df,
        _poblacion_df(),
        _filters(anio=(2009, 2009)),
        "Tasa cada 100.000 habitantes",
    )

    assert nombre_metrica == "Defunciones"
    assert fmt == ":,.0f"
    assert result.iloc[0]["valor_metrica"] == 7
    assert any("Población INDEC disponible desde 2010" in advertencia for advertencia in advertencias)


def test_optimize_dtypes_preserves_values_and_reduces_common_dtypes() -> None:
    df = _mortalidad_df()

    result = optimize_dtypes(df)
    result_values = result.copy()
    for col in result_values.select_dtypes(include=["category"]).columns:
        result_values[col] = result_values[col].astype("object")

    pd.testing.assert_frame_equal(result_values, df, check_dtype=False)
    assert str(result["provincia"].dtype) == "category"
    assert str(result["sexo_desc"].dtype) == "category"
    assert result["anio"].dtype.itemsize < df["anio"].dtype.itemsize
    assert result["CUENTA"].dtype.itemsize < df["CUENTA"].dtype.itemsize
