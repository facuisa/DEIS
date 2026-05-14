from ui_components import section_resumen, show_filtered_table, show_kpis
from src.ui.dashboard_general import section_resumen as section_resumen_impl
from src.ui.kpis import show_kpis as show_kpis_impl
from src.ui.tables import show_filtered_table as show_filtered_table_impl


def test_ui_components_reexports_extracted_ui_functions() -> None:
    assert section_resumen is section_resumen_impl
    assert show_filtered_table is show_filtered_table_impl
    assert show_kpis is show_kpis_impl
