import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
pymysql.install_as_MySQLdb()
from utils import login

st.set_page_config(
    page_title="Soccer Central",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

login.generarLogin()

if "usuario" not in st.session_state:
    st.stop()

st.header(" :orange[Inicio]", divider=True)
conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from db_soccercentral.users;', ttl=600)

st.dataframe(df)

# Print results.
#for row in df.itertuples():
#    st.write(f"{row.name} has a :{row.pet}:")


