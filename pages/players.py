import streamlit as st
from utils import login

st.set_page_config(
    page_title="Jugadores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔐 Verificación de sesión
login.generarLogin()
if "usuario" not in st.session_state:
    st.stop()

st.header(" :orange[Jugadores]", divider=True)