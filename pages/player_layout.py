import streamlit as st
from utils import login
import pandas as pd
import numpy as np
import pymysql
pymysql.install_as_MySQLdb()
import datetime



# Función para inicializar la conexión a la base de datos y cachearla
def connect_to_db():
    try:
        # Intentamos obtener la conexión definida en los secrets
        conn = st.connection('mysql', type='sql')
        st.success("Conexión establecida correctamente")
    except Exception as e:
        # Si ocurre algún error, lo capturamos y mostramos un mensaje en la aplicación
        st.error("Error al conectar con la base de datos:")
        st.error(e) 
    return conn




def Setup_page():
    login.generarLogin()
    # Configuración de la página
    # Configuración título de página.
    # st.set_page_config(page_title="Player Layout Draft", page_icon=":soccer:", 
    #                    layout="centered",initial_sidebar_state="auto",
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



def Show_Player_Info():
    #Este módulo integra la información base del jugador.
    #Se captura data desde DB en AWS con información normalizada.
    #Para la versión actual (MVP) el módulo construido muestra la posible posición de información básica y del perfil del jugador.
    #Versiones posteriores podrían facilitar una configuración personalizable por el usuario.
    # Se espera revisión de contenido y posible look and feel con el cliente para la versión final.
    
    # Conexión a DB*******************
    dbconn = connect_to_db()
       
    #Preparación de la página**********************************************************************
    st.header("360° DATA PLAYER LAYOUT", divider="gray")
    # Mostrar la foto del jugador.
    #st.image("https://media.gettyimages.com/id/1365815844/es/foto/mexico-city-mexico-argentina-captain-diego-maradona-pictured-before-the-fifa-1986-world-cup.jpg?s=612x612&w=gi&k=20&c=vmUfSD2BY0_TQqFi8btORJj6OlNIBTvhkq1RrsY9kV4=", width=300)
    
   
    # El Usuario podrá escoger el jugador por el player_id.
    # Obtener la lista de player_id desde la tabla players
    df_plyid = dbconn.query("SELECT player_id FROM players", ttl=3600)
    player_ids = df_plyid["player_id"].tolist()
    # Crear un widget en el sidebar para que el usuario seleccione el player_id
    selected_player_id = st.sidebar.selectbox("Choose Player", player_ids)
    
    #***********************Preparación de Consulta de Datos Personalizada y Elementos a Visualizar*************************************************************
    # Se seleccionan campos de la tabla "users" y la tabla "players".
    # Si se requieren otros campos o de otras tablas, se pueden agregar al SELECT y al JOIN.
    sql = """
    SELECT 
        u.user_id,
        u.first_name,
        u.last_name,
        u.birth_date,
        u.gender,
        u.photo_url,
        u.phone,
        p.player_id,
        p.nationality,
        p.city,
        p.number,
        p.dominant_foot,
        p.primary_position,
        p.secondary_position,
        p.height,
        s.player_id,            
        s.goals,
        s.minutes_played
    FROM 
        users AS u
    JOIN 
        players AS p ON u.user_id = p.user_id
    JOIN
        player_game_stats AS s ON p.player_id = s.player_id
    WHERE
        p.player_id = :player_id
    """
    #****************Capturando consulta de data 360° del jugador en DataFrame********************************************************
    # --- Ejecución de la consulta ---
    try:
        df = dbconn.query(sql, params={"player_id": selected_player_id}, ttl=3600)
        # Define los nombres de las columnas según el SELECT de tu consulta
        columnas = [
            "user_id", "first_name", "last_name", "birth_date", "gender", "photo_url", "phone",
            "player_id", "nationality", "city", "number", "dominant_foot", "primary_position",
            "secondary_position", "height", "stats_player_id", "goals", "minutes_played"
        ]
        # Creando dataframe para utilizar en visualizador con Data Elements  
        #df2 = pd.DataFrame(df, columns=columnas)
    except Exception as e:
        st.error(f"Error durante la consulta: {e}")

    #************************Preparación elementos a visualizar y otros campos calculados*************************************************************
    if not df.empty:
        # Convertir la primera fila a diccionario
        registro = df.iloc[0].to_dict()
        #Capturar Foto del Jugador.
        if registro.get("photo_url"):
            #st.image(
            #    registro["photo_url"],
            #    caption=f"Player {registro.get('first_name', 'Player')} {registro.get('last_name','')}",
            #    width= 350
            #)
            st.image("https://media.gettyimages.com/id/1365815844/es/foto/mexico-city-mexico-argentina-captain-diego-maradona-pictured-before-the-fifa-1986-world-cup.jpg?s=612x612&w=gi&k=20&c=vmUfSD2BY0_TQqFi8btORJj6OlNIBTvhkq1RrsY9kV4=", width=300)
        else:
            st.info("No se encontró imagen para este jugador.")
        #Incluir más campos calculados como Edad + Gol Avg/90.
        # Calcular Edad
        birth_date = registro['birth_date']
        today = datetime.datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        # Agregar el campo calculado al diccionario
        registro['age'] = age
        #Calcular Gol/90
        if registro['minutes_played'] > 0:
            goals_90 = (registro['goals'] / registro['minutes_played']) * 90
        else:
            goals_90 = 0
        # Agregar el campo calculado al diccionario
        registro['goals_90'] = goals_90
        #registro

        # Separar campos para visualizadores
        general_fields = {
            "Last Name": registro["last_name"],
            #"User ID": registro["user_id"],
            "First Name": registro["first_name"],
            "Birth Date": registro["birth_date"],
            "Age": registro["age"],
            "Gender": registro["gender"],
            "Nationality": registro["nationality"],
            "City": registro["city"],            
            "Contact Phone": registro["phone"]
        }
        profile_fields = {
            "Number": registro["number"],
            "Dominant Foot": registro["dominant_foot"],
            "Primary Position": registro["primary_position"],
            "Secondary Position": registro["secondary_position"],
            "Height": registro["height"],
            "Minutes Played": registro["minutes_played"],
            "Goals": registro["goals"],
            "Goals/90": registro["goals_90"]
        }
        
    else:
        st.info("No se encontraron datos para mostrar.")
    
    # Organizar las tablas en una cuadrícula de 2x2 usando st.columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("GENERAL INFO", divider="red")
        st.table(general_fields)
    with col2:
        st.subheader("PLAYER PROFILE & STATS", divider="red")
        st.table(profile_fields)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("GENERAL INFO", divider="red")
        st.table(general_fields)
    with col4:
        st.subheader("PLAYER PROFILE & STATS", divider="red")
        st.table(profile_fields)

#******************Valorar Construcción para incluir Vídeos y Actividad en Competiciones********************************
              



def main():

    Setup_page()
    Show_Player_Info() 

if __name__ == "__main__":
    main() 