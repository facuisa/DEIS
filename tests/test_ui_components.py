import pandas as pd

from ui_components import _fill_metric_na


def test_fill_metric_na_does_not_fill_categorical_columns() -> None:
    df = pd.DataFrame(
        {
            "causa_desc": pd.Series(["A", None], dtype="category"),
            "Defunciones_A": [10.0, None],
            "Defunciones_B": [None, 5.0],
        }
    )

    result = _fill_metric_na(df, ["Defunciones_A", "Defunciones_B"])

    assert str(result["causa_desc"].dtype) == "category"
    assert result["causa_desc"].isna().sum() == 1
    assert result["Defunciones_A"].tolist() == [10.0, 0.0]
    assert result["Defunciones_B"].tolist() == [0.0, 5.0]
