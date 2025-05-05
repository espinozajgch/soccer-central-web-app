import streamlit as st

# Espaciado superior
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# Título centrado
#st.markdown("<h1 style='text-align: center;'>Home</h1>", unsafe_allow_html=True)

# Espaciado entre título e imagen
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# Imagen centrada
st.image("assets/images/soccer-central.png", width=400)

# Centrar la imagen aplicando CSS
st.markdown(
    """
    <style>
    .stImage > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        padding-left: 1150px; 
    }
    </style>
    """,
    unsafe_allow_html=True
)
