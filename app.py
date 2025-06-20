import streamlit as st
from utils.util import setup_page, iniciar_sesion_si_necesario
import pandas as pd
import numpy as np


# PRIMERO: set_page_config
setup_page("Soccer Central")

# SEGUNDO: login
iniciar_sesion_si_necesario()

# Primero configuramos los componentes de la pagina y luego llamamos a login configurando las cookie
# Carga con la cookie
# Llama a generarLogin()
# Streamlit ya inicializa el frontend
# Solo se llama set_page() la primera vez porque sino set_page() se volveria  ejecutar y falla

st.header(":orange[Home]", divider=True)

a, b, c ,d  = st.columns(4)

a.metric("Temperature", "30°F", "-9°F", border=True)
b.metric("Wind", "4 mph", "2 mph", border=True)

c.metric("Humidity", "77%", "5%", border=True)
d.metric("Pressure", "30.34 inHg", "-2 inHg", border=True)

st.divider()
e, f  = st.columns(2)
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

e.area_chart(chart_data)

#st.divider()

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

f.bar_chart(chart_data)