import streamlit as st
from utils.util import util

util.setup_page("Player Evaluation")

# LOGIN + MENU
util.iniciar_sesion_si_necesario()

st.header(":blue[Byga] Evaluation", divider=True)
