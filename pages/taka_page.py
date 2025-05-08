import streamlit as st
from utils import login
login.generarLogin()

if "usuario" not in st.session_state:
    st.stop()

st.set_page_config(
    page_title="Taka",
    page_icon=":material/videocam:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header('Taka')