import streamlit as st
from utils import util
import pandas as pd
import numpy as np

util.setup_page("Soccer Central")

st.header(" :orange[Home]", divider=True)

a, b, c ,d  = st.columns(4)
#c, d = st.columns(2)

a.metric("Temperature", "30°F", "-9°F", border=True)
b.metric("Wind", "4 mph", "2 mph", border=True)

c.metric("Humidity", "77%", "5%", border=True)
d.metric("Pressure", "30.34 inHg", "-2 inHg", border=True)

st.divider()

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.area_chart(chart_data)