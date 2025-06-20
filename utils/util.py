import streamlit as st

# Cambiamos setup; 
# 1. Separamos el login de la carga de la app
# 2. Solo llamamos a setup la primera vez, el resto mantiene sesion la cookie

def setup_page(title):
    st.set_page_config(
        page_title=title,
        page_icon="assets/images/icon.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def iniciar_sesion_si_necesario():
    from utils import login  # se mete el import aqui, ya que si lo meto arriba se carga (EncryptedCookieManager, session_state) en import y falla, para que set_page_config sea el primer comando
    login.generarLogin()
    if "usuario" not in st.session_state:
        st.stop()

def get_brand_colors_list():
    return ['#d4bc64', '#84ccb4', '#5c74b4', '#6c6c84', '#504f8f', '#83c3d4', '#646c84', '#646c7c', '#588898', '#586c9c']
