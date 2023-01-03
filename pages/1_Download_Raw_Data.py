import streamlit as st
import pandas as pd
# import time

# Packages for Data Extract
# import sqlalchemy as db
import psycopg2
import xlsxwriter

# Packages for Download
import io


# Page Configuration
st.set_page_config(layout="wide")

# Initialize State
# if "load_state" not in st.session_state:
#    st.session_state.load_state = False

# st.write(st.session_state)

# Load SQL Engine
# For better connection use this
# https://docs.streamlit.io/knowledge-base/tutorials/databases/postgresql


@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


connection = init_connection()

# Get Tables and Column Names to Extract
view1_columns = pd.read_csv('input/view6_columns.csv')
view_1_table_names = view1_columns['table_name'].unique().tolist()


# Functions
def reset_button():
    st.session_state["download_check1"] = False
    st.session_state["download_check2"] = False
    return


def fetch_results(sql, conn):
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=columns)
    cur.close()
    return df


def get_input_nct_ids(list_nct_id):
    list_nct_id = input_nct_ids.nct_id.to_list()
    nct_string = "('" + "', '".join([str(elem) for elem in list_nct_id]) + "')"
    return nct_string


def get_ctti_table(table_name):
    # takes the table name and the required NCt Ids that the use provide
    # Returns the Filtered tables

    nct_ids_string = get_input_nct_ids(input_nct_ids)

    ctti_cols = view1_columns[view1_columns['table_name'] == table_name]['column_name'].to_list()
    ctti_cols_string = ','.join([str(elem) for elem in ctti_cols])

    query_string = 'SELECT ' + ctti_cols_string + ' from ' + table_name + ' where nct_id in ' + nct_ids_string

    # ctti_table = pd.read_sql(query_string, engine)
    ctti_table = fetch_results(sql=query_string, conn=connection)

    return ctti_table


def export_ctti_tables():
    buffer = io.BytesIO()
    # this works - https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/16
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    # writer = pd.ExcelWriter('output/selected_CTTI_tables.xlsx', engine='xlsxwriter')

    for tbl_name in view_1_table_names:
        sel_table = get_ctti_table(table_name=tbl_name)
        sel_table.to_excel(writer, sheet_name=tbl_name, index=False)
        sel_table.to_csv('output/csv/' + tbl_name + '.csv', index=False)

    writer.save()
    return buffer


def download_button_xlsx():
    st.markdown("# 2/ Download Raw Data from Clinical Trials Database")
    with st.spinner("Please wait ... "):
        export_buffer = export_ctti_tables()
        st.download_button(
            label="Download Excel workbook",
            data=export_buffer,
            file_name="output/selected_CTTI_tables.xlsx",
            mime="application/vnd.ms-excel",
            on_click=reset_button
        )

# App Start


st.markdown("# 0/ Own Project or Sample Project")
sample_project_checked = st.checkbox("use Sample Project")


if sample_project_checked:
    # Use Sample Data for testing Purpose
    @st.cache
    def data_upload():
        df = pd.read_csv('input/input_nct_ids.csv')
        return df

    input_nct_ids = data_upload()

    st.markdown("# 1/ Already Uploaded Sample Data")
    st.warning(get_input_nct_ids(input_nct_ids.nct_id.to_list()))

    begin_checked = st.checkbox("Click to Start Download Process", key='download_check1')

    if begin_checked:
        download_button_xlsx()

else:
    # Use this space to upload NCT Ids and get User Generated Output
    st.markdown("# 1/ Upload NCT Ids")

    # Take User Upload
    uploaded_raw_nct_ids = st.file_uploader('Please ensure the table contains only one column with "nct_id" as column')

    if uploaded_raw_nct_ids is not None:
        df_nct_ids = pd.read_csv(uploaded_raw_nct_ids, header=0)
        # st.write(df_nct_ids)
        input_nct_ids = df_nct_ids
        st.warning(get_input_nct_ids(input_nct_ids))

        begin_checked = st.checkbox("Click to Start Download Process", key='download_check2')

        if begin_checked:
            download_button_xlsx()

    else:
        st.warning("No NCT Ids Uploaded")
