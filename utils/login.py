import streamlit as st
import logging
import jwt
import datetime
from auth import get_user
from db.db import check_password, hash_password, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.models import Users

# --- CONFIG JWT ---
JWT_SECRET = st.secrets.auth.jwt_secret
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600 * 24 * 1  # 1 días par amatenr la sesion

# Validación simple de usuario y clave
def validarUsuario(usuario, clave):
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    try:
        user_db = get_user(usuario)
    except SQLAlchemyError as e:
        logging.error("Error al conectar con la base de datos", exc_info=True)
        st.error(" No se puede realizar el login en estos momentos.")
        st.stop()
        
    if user_db is None:
        st.session_state.login_attempts += 1
        return False

    stored_pass = user_db.password_hash

    if st.session_state.login_attempts > 5:
        st.error("Demasiados intentos. Intenta más tarde.")
        return False
    else:
        if stored_pass and check_password(clave, stored_pass):
            st.session_state.usuario = user_db
            # Guardar token JWT en sesión
            token = generar_jwt(usuario)
            st.session_state.jwt_token = token
            return True
        else:
            st.session_state.login_attempts += 1
            return False

def generarMenu(usuario):
    with st.sidebar:
        st.logo("assets/images/soccer-central.png", size="large")
        nombre = usuario
        st.write(f"Hello **:blue-background[{nombre}]** ")

        st.page_link("app.py", label="Home", icon=":material/home:")
        st.subheader(":material/dashboard: Dashboard")
        st.page_link("pages/player360.py", label="Player 360", icon=":material/contacts:")
        st.page_link("pages/player_evaluation.py", label="Player Evaluation", icon=":material/description:")
        st.page_link("pages/sc_player_evaluation.py", label="DEMO Player Evaluation", icon=":material/description:")

        st.subheader(":material/manage_accounts: Administrator")
    
        st.page_link("pages/taka_page.py", label="Taka", icon=":material/videocam:")
        current_user = get_logged_in_user()
        if current_user and current_user.role_id != 4:
            st.page_link("pages/user_admin.py", label="User Management", icon=":material/account_circle:")

        st.divider()

        btnSalir = st.button("Salir", type="tertiary", icon=":material/logout:")
        if btnSalir:
            cerrarSesion()

#Cerrar sesión
def cerrarSesion():
    if 'usuario' in st.session_state:
        del st.session_state['usuario']
    if 'jwt_token' in st.session_state:
        del st.session_state['jwt_token']
    st.query_params.clear()
    st.session_state.clear()
    st.cache_data.clear()
    st.cache_resource.clear()
    st.switch_page("App.py")
    st.rerun()

def generarLogin():
    # Si ya hay token, decodificarlo
    if 'jwt_token' in st.session_state:
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
            if 'usuario' in st.session_state:
                del st.session_state["usuario"]

    # Restaurar desde URL
    usuario_actual = st.query_params.get("user")
    if usuario_actual and "usuario" not in st.session_state:
        st.session_state['usuario'] = usuario_actual[0]

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

def generar_jwt(usuario):
    payload = {
        "email": usuario,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def get_logged_in_user():
    if "usuario" not in st.session_state:
        return None

    with Session(engine) as session:
        return session.query(Users).filter(Users.email == st.session_state["usuario"]).first()
