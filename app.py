import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

