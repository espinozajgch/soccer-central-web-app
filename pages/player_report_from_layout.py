import streamlit as st
from utils import login
import pandas as pd
import numpy as np
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime
from sc_app.queries import player_360
from sc_app.create_report import create_pdf
#from common_utils import radar_chart
import random
import plotly.express as px
import utils.pdf_generator  as generate_player_report


# Función para inicializar la conexión a la base de datos y cachearla
def connect_to_db():
    try:
        # InteXntamos obtener la conexión definida en los secrets
        return st.connection('mysql', type='sql')
        #st.success("Conexión establecida correctamente")
    except Exception as e:
        # Si ocurre algún error, lo capturamos y mostramos un mensaje en la aplicación
        st.error("Error al conectar con la base de datos:")
        st.error(e) 
    return None

# Función para calcular la edad

def calculate_age(birth_date):
    today = datetime.today()
    birth_date = birth_date
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Función para calcular goles por 90 minutos

def calculate_goals_per_90(goals, minutes_played):
    # Verificar si minutes_played es cero para evitar la división por cero
    if minutes_played == 0:
        return 0
    # Calcular goles por 90 minutos
    goals_per_90 = (goals / minutes_played) * 90
    return goals_per_90

def Setup_page():
    login.generarLogin()
    # Configuración de la página
    #Configuración título de página.
    #st.set_page_config(page_title="360° PLAYER DATA LAYOUT", page_icon=":soccer:", 
    #                    layout="wide",initial_sidebar_state="auto",
    #                    menu_items={
    #                        'Get Help': 'https://soccercentralsa.byga.net',
    #                        'About': """
    #                             ## Acerca de la Aplicación
                                
    #                             **Soccer Central Web App** es una aplicación desarrollada para facilitar el análisis del rendimiento deportivo de los jugadores de la academia Soccer Central.
                                
    #                             - **Desarrollado con:** Streamlit  
    #                             - **Versión:** 1.0  
    #                             - **Contacto:** support@soccercentral.com
    #                             """
    #                         }
    #                    )
    #Definición de Título y Descripción de Página
    #Creación del Look and Feel de la Página
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)


    #******************************************Feature Provisional para Demo**************************************************************
    # En el sidebar, el usuario selecciona los colores de fondo para cada panel
    main_bg_color = st.sidebar.color_picker("**Choose Background Color for Principal Panel**", "#EDF4F5")
    sidebar_bg_color = st.sidebar.color_picker("**Choose Background Color for Sidebar Panel**", "#D0DEE2")
    # Inyectando CSS para personalizar los fondos utilizando los colores seleccionados
    st.markdown(
        f"""
        <style>
        /* Contenedor principal */
        [data-testid="stAppViewContainer"] {{
            background-color: {main_bg_color};
            
        }}
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    #**************************************FIN de Feature Provisional para Demo***********************************************************

#*******************************************Demo Radar Chart****************************************************************
def radar_chart():  
    dfx = pd.DataFrame(dict(
    r=[random.randint(0,22),
       random.randint(0,22),
       random.randint(0,22),
       random.randint(0,22),
       random.randint(0,22),
       random.randint(0,22)],
    theta=['On Ball','Intelligence','Shot',
           'Defensive', 'Aerial', 'Physical']))
    fig = px.line_polar(dfx, r='r', theta='theta', line_close=True, template = "plotly_dark")
    return fig
    
#*******************************************FIN Demo Radar Chart****************************************************************


def Show_Player_Info():
    #Este módulo integra la información base del jugador.
    #Se captura data desde DB en AWS con información normalizada.
    #Para la versión actual (MVP) el módulo construido muestra la posible posición de información básica y del perfil del jugador.
    #Versiones posteriores podrían facilitar una configuración personalizable por el usuario.
    # Se espera revisión de contenido y posible look and feel con el cliente para la versión final.
    
    # Conexión a DB*******************
    dbconn = connect_to_db()
       
    #Preparación de la página**********************************************************************
    st.header("360° PLAYER DATA", divider="gray")
    # El Usuario podrá escoger el jugador por el player_id.
    # Obtener la lista de player_id desde la tabla players
    df_plyid = dbconn.query("SELECT player_id FROM players", ttl=3600)
    player_ids = df_plyid["player_id"].tolist()
    # Crear un widget en el sidebar para que el usuario seleccione el player_id
    selected_player_id = st.sidebar.selectbox("Choose Player", player_ids)
    
    #****************Capturando consulta de data 360° del jugador en DataFrame********************************************************
    # --- Ejecución de la consulta ---
    try:
        #Obteniendo resultado de consulta general del jugador
        df = dbconn.query(player_360, params={"player_id": selected_player_id}, ttl=3600)
        df = df.iloc[0] # Capturando el primer registro de la consulta. Existen inconsistencias en la DB para fechas de permanencias en equipos.
    except Exception as e:
        st.error(f"Error durante la consulta: {e}")

    #************************Preparación elementos a visualizar y otros campos calculados*************************************************************
        
    # --- Crear DataFrame de datos personales ---
    df_personal = df[["last_name", "first_name", "birth_date", "gender", "photo_url", "nationality", "city", "phone"]]
      # Calcular la edad
    df_personal['age'] = calculate_age(df['birth_date']) 
    
    #Condiciones especiales de manejo de foto por DEMO.****************************************
    
    #Se pasa valor para utilizar luego en creación del PDF.
    #Cargando url de la foto para demo.
    df_personal["photo_url"] = "https://media.gettyimages.com/id/1365815844/es/foto/mexico-city-mexico-argentina-captain-diego-maradona-pictured-before-the-fifa-1986-world-cup.jpg?s=612x612&w=gi&k=20&c=vmUfSD2BY0_TQqFi8btORJj6OlNIBTvhkq1RrsY9kV4=" 
    st.image(df_personal["photo_url"], width=200)
    #Reordenando salida
    df_personal = df_personal[["last_name", "first_name", "age", "birth_date", "gender", "nationality", "city", "phone"]]

    # --- Organizando datos de perfil del jugador ---
    df_profile = df[["name", "number", "dominant_foot", "primary_position", "secondary_position", "height", "games_played", "total_minutes_played", "starter_games", "goals"]]
    #Calcular Gol por 90 minutos
    df_profile['goals_per_90'] = calculate_goals_per_90(df_profile["goals"], df_profile["total_minutes_played"])
        
    df_info1 = df_personal #Uso en creación de PDF
    df_info2 = df_profile  #Uso en creación de PDF

    #Preparando Info de Salida 
    #df_personal
    df_personal = df_personal.reset_index()
    df_personal.columns = ["Personal Info", ""]

    df_profile = df_profile.reset_index()
    df_profile.columns = ["Profile", ""]
    # Organizar las tablas en una cuadrícula de 2x2 usando st.columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("GENERAL INFO", divider="red")
        # Aplicando estilo para ocultar la cabecera
        st.dataframe(df_personal, hide_index=True)
    with col2:
        st.subheader("PLAYER PROFILE & STATS", divider="red")
        st.dataframe(df_profile, hide_index=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("PLAYER PERFORMANCE", divider="green")
        #st.plotly_chart(radar_chart(), use_container_width=True)    
        placeholder = st.empty()
        placeholder.write(radar_chart())
    with col4:
        st.subheader("ANALYSIS BY SKILLS", divider="blue")
        data = {
            "Skill": ["On Ball", "Intelligence", "Shot", "Defensive", "Aerial", "Physical"],
            "Description": [
                "Displays exceptional ball control and agility when dribbling.",
                "Exhibits outstanding game vision and anticipates plays effectively.",
                "Possesses a powerful and accurate shot, making the most of scoring opportunities.",
                "Shows solid defensive strategies with impressive marking and interception skills.",
                "Excels in aerial duels, leveraging timing and positioning to win headers.",
                "Demonstrates superior physical strength and endurance in duels."
            ]
        }
        df_an = pd.DataFrame(data)
        st.dataframe(df_an, hide_index=True)
       
#*********************************FIN Show_Player_Info()*********************************************************

    # En el sidebar, se coloca un botón para generar el informe PDF
    empty_df = pd.DataFrame()

    player_data = {
        "first_name": df["first_name"],
        "last_name": df["last_name"],
        "birth_date": df["birth_date"],
        "nationality": df["nationality"],
        "primary_position": df["primary_position"],
        "secondary_position": df["secondary_position"],
        "number": df["number"],
        "dominant_foot": df["dominant_foot"],
        "height": df["height"],
        "education_level": "High School",
        "school_name": "Soccer Central Academy",
        "photo_url": df["photo_url"],
        "notes": df.get("notes", ""),
        "player_activity_history": df.get("player_activity_history", "")
    }

    pdf_buffer = generate_player_report.generate_player_report(
        player_data=player_data,
        player_teams=empty_df,
        player_games=empty_df,
        player_metrics=empty_df,
        player_evaluations=empty_df,
        player_videos=empty_df,
        player_documents=empty_df
    )

    st.download_button(
        label="📄 Generate & Download PDF Report",
        data=pdf_buffer,
        file_name=f"player_report_{player_data['last_name']}.pdf",
        mime="application/pdf"
    )


def main():

    Setup_page()
    Show_Player_Info() 

if __name__ == "__main__":
    main() 