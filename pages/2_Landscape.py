import pandas as pd
import streamlit as st
import psycopg2

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(layout="wide")


@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


def fetch_results(sql, conn):
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=columns)
    cur.close()
    return df


connection = init_connection()


sql_query_string = "select * from countries limit 5"
ctti_df = fetch_results(sql=sql_query_string, conn=connection)
st.write(ctti_df.head())
