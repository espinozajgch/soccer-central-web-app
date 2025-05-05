import streamlit as st
from sc_app.auth import hash_password, check_password
from sc_app.db import init_db, add_user, get_user

init_db()

st.title("🔐 SC App - Login")

menu = st.sidebar.selectbox("Opciones", ["Login", "Registrarse", "Recuperar contraseña"])

if menu == "Login":
    st.subheader("Iniciar sesión")
    user = st.text_input("Usuario")
    passwd = st.text_input("Contraseña", type="password")
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0

    if st.button("Ingresar"):
        stored_pass = get_user(user)
        if st.session_state.login_attempts > 5:
            st.error("Demasiados intentos. Intenta más tarde.")
        else:
            if stored_pass and check_password(passwd, stored_pass):
                st.success(f"Bienvenido {user}")
            else:
                st.session_state.login_attempts += 1
                st.error("Usuario o contraseña incorrectos")

elif menu == "Registrarse":
    st.subheader("Crear cuenta")
    new_user = st.text_input("Nuevo usuario")
    new_pass = st.text_input("Nueva contraseña", type="password")
    if st.button("Registrar"):
        hashed = hash_password(new_pass)
        try:
            add_user(new_user, hashed)
            st.success("Usuario registrado con éxito")
        except:
            st.error("Ese usuario ya existe")

elif menu == "Recuperar contraseña":
    st.subheader("Recuperar contraseña")
    user = st.text_input("Usuario")
    st.info("Funcionalidad simulada. En producción deberías enviar un correo o enlace seguro.")