"""Tablas del dashboard general."""

import pandas as pd
import streamlit as st

from src.analysis.aggregations import filtered_table_aggregate


def show_filtered_table(df: pd.DataFrame, nombre_metrica: str = "Defunciones") -> None:
    st.markdown('<div class="section-header">E · Tabla de Datos Filtrados</div>', unsafe_allow_html=True)

    with st.expander("Ver tabla de datos (filtrada)", expanded=False):
        if nombre_metrica != "Defunciones":
            st.info("ℹ️ En modo **Tasa c/100k**, se muestra la vista agregada.")
            vista = "Agregada por causa y año"
        else:
            vista = st.radio("Modo de vista:", ["Agregada por causa y año", "Registros crudos (primeros 2.000)"], horizontal=True)

        if vista == "Agregada por causa y año":
            group_cols = [c for c in ["anio", "provincia", "CAUSA_grupo_macro", "causa_desc", "sexo_desc"] if c in df.columns]
            show_df = filtered_table_aggregate(df, group_cols).rename(columns={"valor_metrica": nombre_metrica})
        else:
            show_df = df.head(2_000).copy().rename(columns={"valor_metrica": nombre_metrica})

        # Usamos el buscador nativo de Streamlit que es más eficiente
        st.dataframe(show_df, use_container_width=True, height=400)

        csv_export = show_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV filtrado completo", csv_export, "mortalidad_filtrado.csv", "text/csv")
