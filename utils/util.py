import streamlit as st
from utils import login

def setup_page(title):
    setup_config(title)
    login.generarLogin()

    if "usuario" not in st.session_state:
        st.stop()

def setup_config(title):
    st.set_page_config(
        page_title=title,
        page_icon="assets/images/icon.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )