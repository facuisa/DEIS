from data_processing import apply_filters, calcular_metrica
from src.domain.filters import apply_filters as domain_apply_filters
from src.domain.metrics import calcular_metrica as domain_calcular_metrica


def test_data_processing_reexports_domain_functions() -> None:
    assert apply_filters is domain_apply_filters
    assert calcular_metrica is domain_calcular_metrica
