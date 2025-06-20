import streamlit as st
from utils.util import util

util.setup_page("Player Evaluation")

# LOGIN + MENU
util.login_if_needed()

st.header(":blue[Byga] Evaluation", divider=True)
