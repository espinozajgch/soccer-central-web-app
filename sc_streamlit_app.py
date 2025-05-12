import streamlit as st

# --- SHARED ON ALL PAGES ---
with st.sidebar:
    st.logo("assets/images/soccer-central.png")

# --- PAGE SETUP ---
home_page = st.Page(
    "pages/home_page.py",
    title="Home",
    icon=":material/home:",
    default=True,
)

about_page = st.Page(
    "pages/taka_page.py",
    title="Taka",
    icon=":material/videocam:",

)
project_1_page = st.Page(
    "pages/byga_page.py",
    title="Byga",
    icon=":material/analytics:",
)
project_2_page = st.Page(
    "pages/Achamp_page.py",
    title="A-Champ",
    icon=":material/sports_and_outdoors:",
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Home": [home_page],
        "Projects": [about_page, project_1_page, project_2_page],
    }
)

# --- RUN NAVIGATION ---
pg.run()