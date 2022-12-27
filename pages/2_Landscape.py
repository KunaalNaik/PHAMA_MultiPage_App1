import pandas as pd
import streamlit as st
import psycopg2

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


conn = init_connection()


sql = "select * from countries limit 5"
df = fetch_results(sql=sql, conn=conn)
st.write(df.head)
