import streamlit as st
#import pandas as pd
#Variables para manejo de DB
#from sqlalchemy import create_engine, inspect


def Setup_page():
    # Configuración de la página
    # Configuración título de página.
    st.set_page_config(page_title="Player Layout Draft", page_icon=":soccer:", 
                       layout="centered",initial_sidebar_state="auto",
                       menu_items={
                           'Get Help': 'https://soccercentralsa.byga.net',
                           'About': """
                                ## Acerca de la Aplicación
                                
                                **Soccer Central Web App** es una aplicación desarrollada para facilitar el análisis del rendimiento deportivo de los jugadores de la academia Soccer Central.
                                
                                - **Desarrollado con:** Streamlit  
                                - **Versión:** 1.0  
                                - **Contacto:** support@soccercentral.com
                                """
                            }
                       )
    #Definición de Título y Descripción de Página
    #Creación del Look and Feel de la Página
    logo = "./images/soccer-central.png"
    st.sidebar.image(logo, width=350)
    

    #Feature Provisional para Demo
    # En el sidebar, el usuario selecciona los colores de fondo para cada panel
    main_bg_color = st.sidebar.color_picker("**Choose Background Color for Principal Panel**", "#646C84")
    sidebar_bg_color = st.sidebar.color_picker("**Choose Background Color for Sidebar Panel**", "#D0DEE2")
    # Inyectando CSS para personalizar los fondos utilizando los colores seleccionados
    st.markdown(
        f"""
        <style>
        /* Contenedor principal */
        [data-testid="stAppViewContainer"] {{
            background-color: {main_bg_color};
            padding: 1rem;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    #FIN de Feature Provisional para Demo



def Show_Player_Info():
    #Este módulo integra la información base del jugador (DRAFT version).
    #Se estaría capturando la misma desde la DB con la información normalizada.
    #En Módulo actual Únicamente se muestra la posible posición de información básica del jugador y el club.
    # Se espera revisión de contenido y posible look and feel con el cliente para la versión final.

    
    st.header("BASIC PLAYER INFO DEMO", divider="gray")
    
     # Mostrar la foto del jugador.
    st.image("./images/player-demo.jpg", width=250)
    # Crear dos columnas: panel izquierdo (datos personales y foto), 
    # panel derecho (datos con mayor enfoque al seguimiento por la academia).
    col_left, col_right = st.columns(2)

    # Panel Izquierdo: Información Personal del Jugador junto a la foto.
    with col_left:
        # Abrimos el contenedor HTML para enmarcar el contenido del panel izquierdo
             # Título del panel
            st.markdown(
            """
            <div style="
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
                background-color: #FFFFFF;">
                <h3 style="text-align: center;">PLAYER INFO</h3>
                <p><strong>NAME:</strong> Player X Y</p>
                <p><strong>AGE:</strong> 16 Years</p>
                <p><strong>GENDER:</strong> F/M</p>
                <p><strong>NATIONALITY:</strong> USA</p>
                <p><strong>BIRTH DATE:</strong> mm/dd/yyyy</p>
            </div>
            """,
            unsafe_allow_html=True
            )            
        
    # Panel Derecho: Club Info.
    with col_right:
        st.markdown(
        """
        <div style="
            border: 2px solid #333333;
            border-radius: 10px;
            padding: 20px;
            margin: 10px;
            background-color: #FFFFFF;">
            <h3 style="text-align: center;">CLUB INFO</h3>
            <p><strong>TEAM:</strong> MLS Next</p>
            <p><strong>AGE GROUP:</strong> U-16</p>
            <p><strong>PRYMARY POSITION:</strong> FW</p>
            <p><strong>SECONDARY POSITION:</strong> MDF</p>
            <p><strong>NUMBER:</strong> N°9</p>
            <p><strong>DOMINANT FOOT :</strong> LEFT</p>
            <p><strong>HEIGHT:</strong> 1.72 m</p>
            <p><strong>WEIGHT:</strong> 65 kg</p>
        </div>
        """,
        unsafe_allow_html=True
        )
  
def main():
    
    Setup_page()
    Show_Player_Info() 
    
if __name__ == "__main__":
    main() 
    