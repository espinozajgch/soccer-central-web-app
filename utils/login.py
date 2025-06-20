# utils/login.py

import streamlit as st
import logging
import jwt
import datetime
from auth import get_user
from db.db import check_password, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.models import Users
from streamlit_cookies_manager import EncryptedCookieManager

# --- CONFIG JWT ---
JWT_SECRET = st.secrets.auth.jwt_secret
JWT_ALGORITHM = st.secrets.auth.algorithm
JWT_EXP_DELTA_SECONDS = 3600 * 24 * 1  # 1 día

# --- FUNCION PARA CREAR COOKIES ---
def get_cookies():
    cookies = EncryptedCookieManager(
        prefix="sc_",
        password=JWT_SECRET
    )
    if not cookies.ready():
        st.stop()
    return cookies

# --- VALIDACIÓN DE USUARIO ---
def validarUsuario(usuario, clave):
    cookies = get_cookies()

    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0

    try:
        user_db = get_user(usuario)
    except SQLAlchemyError:
        logging.error("Error DB", exc_info=True)
        st.error("No se puede realizar el login.")
        st.stop()

    if user_db is None:
        st.session_state.login_attempts += 1
        return False

    if st.session_state.login_attempts > 5:
        st.error("Demasiados intentos. Intenta más tarde.")
        return False

    if check_password(clave, user_db.password_hash):
        st.session_state.usuario = user_db
        token = generar_jwt(usuario)
        st.session_state.jwt_token = token
        cookies["jwt_token"] = token
        cookies.save()
        return True
    else:
        st.session_state.login_attempts += 1
        return False

# --- JWT ---
def generar_jwt(usuario):
    payload = {
        "email": usuario,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# --- GET USUARIO LOGUEADO ---
def get_logged_in_user():
    if "usuario" not in st.session_state:
        return None

    with Session(engine) as session:
        return session.query(Users).filter(Users.email == st.session_state["usuario"]).first()

# --- MENU ---
def generarMenu(usuario):
    with st.sidebar:
        st.logo("assets/images/soccer-central.png", size="large")
        st.write(f"Hello **:blue-background[{usuario}]** ")

        st.page_link("app.py", label="Home", icon=":material/home:")
        st.subheader(":material/dashboard: Dashboard")
        st.page_link("pages/player360.py", label="Player 360", icon=":material/contacts:")
        st.page_link("pages/player_evaluation.py", label="Player Evaluation", icon=":material/description:")
        st.page_link("pages/sc_player_evaluation.py", label="DEMO Player Evaluation", icon=":material/description:")

        st.subheader(":material/manage_accounts: Administrator")
    
        current_user = get_logged_in_user()
        if current_user and current_user.role_id != 4:
            st.page_link("pages/user_admin.py", label="User Management", icon=":material/account_circle:")

        st.divider()

        btnSalir = st.button("Log out", type="tertiary", icon=":material/logout:")
        if btnSalir:
            cerrarSesion()

# --- CERRAR SESION ---
def cerrarSesion():
    cookies = get_cookies()

    if 'usuario' in st.session_state:
        del st.session_state['usuario']
    if 'jwt_token' in st.session_state:
        del st.session_state['jwt_token']
    if "jwt_token" in cookies:
        del cookies["jwt_token"]
        cookies.save()

    st.query_params.clear()
    st.session_state.clear()
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page("App.py")
    st.rerun()

# --- GENERAR LOGIN ---
def generarLogin():
    cookies = get_cookies()

    # 1️⃣ Intentar recuperar JWT desde cookie
    if "jwt_token" not in st.session_state and "jwt_token" in cookies:
        st.session_state.jwt_token = cookies["jwt_token"]

    # 2️⃣ Validar token JWT
    if "jwt_token" in st.session_state:
        try:
            payload = jwt.decode(
                st.session_state.jwt_token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            email = payload.get("email")
            if email and "usuario" not in st.session_state:
                st.session_state["usuario"] = email
        except jwt.ExpiredSignatureError:
            st.warning("Sesión expirada, vuelve a iniciar sesión.")
            del st.session_state["jwt_token"]
            if "jwt_token" in cookies:
                del cookies["jwt_token"]
                cookies.save()
            if 'usuario' in st.session_state:
                del st.session_state["usuario"]

    # 3️⃣ Validar URL query param
    usuario_actual = st.query_params.get("user")
    if usuario_actual and "usuario" not in st.session_state:
        st.session_state['usuario'] = usuario_actual[0]

    # 4️⃣ Mostrar menú o login
    if 'usuario' in st.session_state:
        st.query_params.update({"user": [st.session_state["usuario"]]})
        generarMenu(st.session_state['usuario'])
    else:
        st.logo("assets/images/soccer-central.png", size="large")
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col2:
            with st.form('frmLogin'):
                parUsuario = st.text_input('Usuario')
                parPassword = st.text_input('Password', type='password')
                btnLogin = st.form_submit_button('Ingresar', type='primary')

                if btnLogin:
                    if validarUsuario(parUsuario, parPassword):
                        st.session_state['usuario'] = parUsuario
                        st.query_params.update({'user': [parUsuario]})
                        st.rerun()
                    else:
                        st.error("Usuario o clave inválidos", icon=":material/gpp_maybe:")
