import streamlit as st
import pandas as pd
import logging
from auth import get_user
from db.db import check_password, hash_password, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.models import Users

# Validación simple de usuario y clave con un archivo csv

def validarUsuario(usuario,clave):    
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """    
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    try:    
        user_db = get_user(usuario)
    except SQLAlchemyError as e:
        logging.error("Error al conectar con la base de datos", exc_info=True)
        st.error(" Lo sentimos, no se puede realizar el login en estos momentos.")
        st.error(" Intentelo de nuevo más tarde.")
        st.stop()  # Detiene la ejecución de la app sin que se caiga
        
    if user_db is None:
        st.session_state.login_attempts += 1
        return False
    stored_pass = user_db.password_hash
    if st.session_state.login_attempts > 5:
        st.error("Demasiados intentos. Intenta más tarde.")
        return False
    else:
        print("Password:" + str(hash_password(clave)))
        if stored_pass and check_password(clave, stored_pass):
            st.session_state.usuario = user_db
            return True
        else:
            st.session_state.login_attempts += 1
            return False

def generarMenu(usuario):
    """Genera el menú dependiendo del usuario

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar:
        st.logo("assets/images/soccer-central.png", size="large")

        # Cargamos la tabla de usuarios
        #dfusuarios = pd.read_csv('usuarios.csv')

        # Filtramos la tabla de usuarios
        #dfUsuario =dfusuarios[(dfusuarios['usuario']==usuario)]
        
        # Cargamos el nombre del usuario
        nombre= usuario
        
        #Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{nombre}]** ")
        
        # Mostramos los enlaces de páginas
        st.page_link("app.py", label="Home", icon=":material/home:")
        st.subheader(":material/dashboard: Dashboard")
        st.page_link("pages/player360.py", label="Player 360", icon=":material/contacts:")
        st.page_link("pages/player_evaluation.py", label="Player Evaluation", icon=":material/description:")
        st.page_link("pages/sc_player_evaluation.py", label="DEMO Player Evaluation", icon=":material/description:")

        st.subheader(":material/manage_accounts: Administrator")

        st.page_link("pages/achamp_page.py", label="Achamps", icon=":material/bar_chart:")
        st.page_link("pages/byga_page.py", label="Byga", icon=":material/sports_soccer:")
        st.page_link("pages/taka_page.py", label="Taka", icon=":material/videocam:")
        
        st.page_link("pages/player_admin.py", label="Players", icon=":material/account_circle:")

        st.divider()

        # Botón para cerrar la sesión
        btnSalir=st.button("Salir", type="tertiary", icon=":material/logout:")
        if btnSalir:
            cerrarSesion()

#Función para cerrar sesión y limpiar query_params
def cerrarSesion():
    if 'usuario' in st.session_state:
        del st.session_state['usuario']
    st.query_params.clear()  #Limpia la URL
    st.session_state.clear()
    st.cache_data.clear()     #Limpia la caché de datos
    st.cache_resource.clear() #Limpia la caché de recursos
    st.switch_page("App.py")  #Para evitar rastros de otras páginas al salir.
    st.rerun()

def generarLogin():

    #Restaurar sesión desde la URL si existe
    usuario_actual = st.query_params.get("user")
    if usuario_actual and "usuario" not in st.session_state:
        st.session_state['usuario'] = usuario_actual['username']

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
                        st.query_params.update({'user': [parUsuario]})  # persistencia en URL
                        st.rerun()
                    else:
                        st.error("Usuario o clave inválidos", icon=":material/gpp_maybe:")

def get_logged_in_user():
    if "usuario" not in st.session_state:
        return None

    with Session(engine) as session:
        return session.query(Users).filter(Users.email == st.session_state["usuario"]).first()

