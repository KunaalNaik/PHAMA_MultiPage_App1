import streamlit as st
import pandas as pd
import io

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

import plotly
pd.options.plotting.backend = "plotly"

st.set_page_config(layout="wide")


# @st.cache
def data_upload():
    df = pd.read_csv('views/view_geography.csv')
    return df


def display_table(table_name):
    gd = GridOptionsBuilder.from_dataframe(table_name)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(groupable=True)  # editable=True
    gd.build()
    return AgGrid(table_name)


def reset_button():
    st.session_state["download_check1"] = False
    st.session_state["download_check2"] = False
    return


def export_ctti_tables():
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    sel_table = data_upload()
    sel_table.to_excel(writer, sheet_name="data", index=False)
    # sel_table.to_csv('output/csv/' + tbl_name + '.csv', index=False)
    writer.save()
    return buffer


def download_button_xlsx(df):
    # st.markdown("# 2/ Data Download")
    with st.spinner("Please wait ... "):
        export_buffer = export_ctti_tables()
        st.download_button(
            label="Download Excel workbook",
            data=export_buffer,
            file_name="output/selected_CTTI_tables.xlsx",
            mime="application/vnd.ms-excel",
            on_click=reset_button
        )


def plot_region_country_count():
    df = data
    df_region = pd.DataFrame(df.drop(['c_mature', 'c_non_mature'], axis=1).filter(regex="c_.*").sum()).reset_index()
    df_region.columns = ['Region', 'Country_Count']
    return df_region.plot.bar(x='Region', y='Country_Count')


data = data_upload()


st.header("Geography")


download_button_xlsx(data)

st.plotly_chart(plot_region_country_count())

display_table(data)
