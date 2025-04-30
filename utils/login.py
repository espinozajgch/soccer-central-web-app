import streamlit as st
import pandas as pd

# Validación simple de usuario y clave con un archivo csv

def validarUsuario(usuario,clave):    
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """    
    dfusuarios = pd.read_csv('usuarios.csv')
    if len(dfusuarios[(dfusuarios['usuario']==usuario) & (dfusuarios['clave']==clave)])>0:
        return True
    else:
        return False

def generarMenu(usuario):
    """Genera el menú dependiendo del usuario

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar:
        st.logo("assets/images/soccer-central.png", size="large")

        # Cargamos la tabla de usuarios
        dfusuarios = pd.read_csv('usuarios.csv')

        # Filtramos la tabla de usuarios
        dfUsuario =dfusuarios[(dfusuarios['usuario']==usuario)]
        
        # Cargamos el nombre del usuario
        nombre= dfUsuario['nombre'].values[0]
        
        #Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{nombre}]** ")
        
        # Mostramos los enlaces de páginas
        st.page_link("app.py", label="Inicio", icon=":material/home:")
        st.subheader(":material/dashboard: Tableros")
        st.page_link("pages/dashboard.py", label="360", icon=":material/contacts:")
        st.subheader(":material/manage_accounts: Administrador")
        st.page_link("pages/players.py", label="Jugadores", icon=":material/account_circle:")
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
    st.rerun()

def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es válido"""    

    #Verificamos si el usuario ya está en la URL o en session_state
    usuario_actual = st.query_params.get("user", None)
    if usuario_actual:
        st.session_state['usuario'] = usuario_actual

    # Si ya hay usuario, mostramos el menú
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario']) 
    else: 
        st.logo("assets/images/soccer-central.png", size="large")
        col1, col2, col3 = st.columns([2, 1.5, 2])
        with col2:
            st.text("¡Bienvenido!")
        
        
        with col2:
            #st.logo("assets/images/soccer-central.png", size="large")
            # Cargamos el formulario de login       
            with st.form('frmLogin'):
                parUsuario = st.text_input('Usuario')
                parPassword = st.text_input('Password', type='password')
                btnLogin = st.form_submit_button('Ingresar', type='primary')

                if btnLogin:
                    if validarUsuario(parUsuario, parPassword):
                        # Guardamos usuario en session_state y en la URL
                        st.session_state['usuario'] = parUsuario
                        st.query_params.user = parUsuario  #Persistencia en la URL
                        st.rerun()
                    else:
                        st.error("Usuario o clave inválidos", icon=":material/gpp_maybe:")


