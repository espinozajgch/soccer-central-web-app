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

def get_brand_colors_list():
    return ['#d4bc64', '#84ccb4', '#5c74b4', '#6c6c84', '#504f8f', '#83c3d4', '#646c84', '#646c7c', '#588898', '#586c9c']
