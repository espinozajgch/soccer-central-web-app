import streamlit as st
from utils import login
import pandas as pd
import numpy as np
from datetime import datetime
from db import SessionLocal
from models import Users, Players, PlayerGameStats

login.generarLogin()

def Show_Player_Info():
    #Este módulo integra la información base del jugador.
    #Se captura data desde DB en AWS con información normalizada.
    #Para la versión actual (MVP) el módulo construido muestra la posible posición de información básica y del perfil del jugador.
    #Versiones posteriores podrían facilitar una configuración personalizable por el usuario.
    # Se espera revisión de contenido y posible look and feel con el cliente para la versión final.
       
    #Preparación de la página**********************************************************************
    st.header("360° PLAYER DATA LAYOUT", divider="gray")
    session = SessionLocal()
    # Mostrar la foto del jugador.
    #st.image("https://media.gettyimages.com/id/1365815844/es/foto/mexico-city-mexico-argentina-captain-diego-maradona-pictured-before-the-fifa-1986-world-cup.jpg?s=612x612&w=gi&k=20&c=vmUfSD2BY0_TQqFi8btORJj6OlNIBTvhkq1RrsY9kV4=", width=300)
    
   
    # El Usuario podrá escoger el jugador por el player_id.
    # Obtener la lista de player_id desde la tabla players

    df_players = session.query(Players).limit(10).all()
    player_ids = [player.player_id for player in df_players]
    # Crear un widget en el sidebar para que el usuario seleccione el player_id
    #selected_player_id = st.sidebar.selectbox("Choose Player", player_ids)
    
    #***********************Preparación de Consulta de Datos Personalizada y Elementos a Visualizar*************************************************************
    # Se seleccionan campos de la tabla "users" y la tabla "players".
    # Si se requieren otros campos o de otras tablas, se pueden agregar al SELECT y al JOIN.
    #****************Capturando consulta de data 360° del jugador en DataFrame********************************************************
    # --- Ejecución de la consulta ---
    # try:
    #     df = player_ids dbconn.query(sql, params={"player_id": selected_player_id}, ttl=3600)
    # except Exception as e:
    #     st.error(f"Error durante la consulta: {e}")
    selected_player_id = 1
    #************************Preparación elementos a visualizar y otros campos calculados*************************************************************
    if selected_player_id:
        # Convertir la primera fila a diccionario
        registro = session.query(Players).filter(Players.player_id == selected_player_id).first()        #Capturar Foto del Jugador.
        if registro.user.photo_url:
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
        birth_date = registro.user.birth_date
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        # Agregar el campo calculado al diccionario
        registro.user.age = age
        stats = session.query(PlayerGameStats).filter_by(player_id=registro.player_id).first()
        #Calcular Gol/90
        if stats.minutes_played > 0:
            goals_90 = (stats.goals / stats.minutes_played) * 90
        else:
            goals_90 = 0
        # Agregar el campo calculado al diccionario
        stats.goals_90 = goals_90
        #registro

        # Separar campos para visualizadores
        general_fields = {
            "Last Name": registro.user.last_name,
            #"User ID": registro.user.user_id,
            "First Name": registro.user.first_name,
            "Birth Date": registro.user.birth_date,
            "Age": registro.user.age,
            "Gender": registro.user.gender,
            "Nationality": registro.nationality,
            "City": registro.city,
            "Contact Phone": registro.user.phone
        }
        profile_fields = {
            "Number": registro.number,
            "Dominant Foot": registro.dominant_foot,
            "Primary Position": registro.primary_position,
            "Secondary Position": registro.secondary_position,
            "Height": registro.height,
            "Minutes Played": stats.minutes_played,
            "Goals": stats.goals,
            "Goals/90": stats.goals_90
        }
        
    else:
        st.info("No se encontraron datos para mostrar.")
    
    #Inyectar CSS personalizado
    st.markdown(
        """
        <style>
        /* Estilos para las claves (labels) */
        .key-text {
            font-size: 26px;
            color: #333333;
            font-weight: bold;
        }
        /* Estilos para los valores */
        .value-text {
            font-size: 24px;
            color: #333333;
        }
        </style>
        """,
        unsafe_allow_html=True
    )   
    
    
    # Crear dos columnas: panel izquierdo (datos personales y foto), 
    # panel derecho (datos con mayor enfoque al seguimiento por la academia).
    col_left, col_right = st.columns(2)

    # Panel Izquierdo: Información Personal del Jugador junto a la foto.
    with col_left:
        col_left.subheader("GENERAL INFO", divider="red")
        with st.container(border=True):
            st.markdown('<div class="custom-container">', unsafe_allow_html=True)
            for key, value in general_fields.items():
                # Cada par clave-valor se muestra en dos columnas:
                key_col, value_col = st.columns([1, 2])
                with key_col:
                    st.markdown(f'<span class="key-text">{key}:</span>', unsafe_allow_html=True)
                with value_col:
                    st.markdown(f'<span class="value-text">{value}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)            
            

    # Panel Derecho: Player Profile & Stats.
    with col_right:
        # Título del panel
        col_right.subheader("PLAYER PROFILE & STATS", divider="red")
        with st.container(border=True):
            st.markdown('<div class="custom-container">', unsafe_allow_html=True)
            for key, value in profile_fields.items():
                # Cada par clave-valor se muestra en dos columnas:
                key_col, value_col = st.columns([1, 2])
                with key_col:
                    st.markdown(f'<span class="key-text">{key}:</span>', unsafe_allow_html=True)
                with value_col:
                    st.markdown(f'<span class="value-text">{value}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

#******************Valorar Construcción para incluir Vídeos y Actividad en Competiciones********************************
              



def main():
    Show_Player_Info() 

if __name__ == "__main__":
    main() 