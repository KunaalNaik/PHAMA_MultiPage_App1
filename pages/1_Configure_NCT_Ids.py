import streamlit as st
import pandas as pd
import time

# Packages for Data Extract
import sqlalchemy as db
import xlsxwriter

# Packages for Download
from io import BytesIO


# Page Configuration
st.set_page_config(layout="wide")


# sample_check = st.checkbox("Check this to get Sample Data")
def get_input_nct_ids(list_nct_id):
    list_nct_id = input_nct_ids.nct_id.to_list()
    nct_string = "('" + "', '".join([str(elem) for elem in list_nct_id]) + "')"
    return nct_string


# Step 1 : Connect and Download raw Data from CTTI Database
# Use this space to upload NCT Ids
st.markdown("# 1/ Upload NCT Ids")

# Option 1 - User Upload
uploaded_nct_ids = st.file_uploader('Please ensure the table contains only one column with "nct_id" as column')
# if uploaded_nct_ids is not None:
#   input_nct_ids = uploaded_nct_ids.nct_id.to_list()
#    st.warning(get_input_nct_ids(input_nct_ids))


# Option 2 - While developement
# sample Data Upload and Stored in Cache
@st.cache
def data_upload():
    df = pd.read_csv('input/input_nct_ids.csv')
    return df


input_nct_ids = data_upload()
st.warning(get_input_nct_ids(input_nct_ids.nct_id.to_list()))


# Download Excel file with all Data

# Load SQL Engine
engine = db.create_engine("postgresql://devikasrinivas:Data1281@aact-db.ctti-clinicaltrials.org:5432/aact")

# Get Tables and Column Names to Extract
view1_columns = pd.read_csv('input/view1_columns.csv')
view_1_table_names = view1_columns['table_name'].unique().tolist()


# Functions
def get_ctti_table(table_name):
    # takes the table name and the required NCt Ids that the use provide
    # Returns the Filtered tables

    nct_ids_string = get_input_nct_ids(input_nct_ids)

    ctti_cols = view1_columns[view1_columns['table_name'] == table_name]['column_name'].to_list()
    ctti_cols_string = ','.join([str(elem) for elem in ctti_cols])

    query_string = 'SELECT ' + ctti_cols_string + ' from ' + table_name + ' where nct_id in ' + nct_ids_string

    ctti_table = pd.read_sql(query_string, engine)

    return ctti_table


def export_ctti_tables():
    buffer = BytesIO()
    # this works - https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/16
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    # writer = pd.ExcelWriter('output/selected_CTTI_tables.xlsx', engine='xlsxwriter')

    for tbl_name in view_1_table_names:
        sel_table = get_ctti_table(table_name=tbl_name)
        sel_table.to_excel(writer, sheet_name=tbl_name, index=False)
        # sel_table.to_csv('output/csv/' + tbl_name + '.csv', index=False)

    writer.save()
    return buffer


st.markdown("# 2/ Download Raw Data from Clinical Trials Database")


with st.spinner("Please wait ... "):
    export_buffer = export_ctti_tables()
    st.download_button(
        label="Download Excel workbook",
        data=export_buffer,
        file_name="output/selected_CTTI_tables.xlsx",
        mime="application/vnd.ms-excel"
    )
