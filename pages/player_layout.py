import streamlit as st
from utils import login
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Users, Players, PlayerGameStats
from db import engine  # Asegúrate de tener configurado tu `engine` SQLAlchemy

def Setup_page():
    login.generarLogin()
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)

    main_bg_color = st.sidebar.color_picker("**Choose Background Color for Principal Panel**", "#EDF4F5")
    sidebar_bg_color = st.sidebar.color_picker("**Choose Background Color for Sidebar Panel**", "#D0DEE2")

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-color: {main_bg_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color};
        }}
        </style>
    """, unsafe_allow_html=True)

def Show_Player_Info():
    st.header("360° DATA PLAYER LAYOUT", divider="gray")

    with Session(engine) as session:
        # Obtener todos los player_id para selección
        player_ids = [p.player_id for p in session.query(Players.player_id).all()]
        selected_player_id = st.sidebar.selectbox("Choose Player", player_ids)

        # Obtener datos del jugador, usuario y estadísticas
        result = (
            session.query(
                Users.user_id,
                Users.first_name,
                Users.last_name,
                Users.birth_date,
                Users.gender,
                Users.photo_url,
                Users.phone,
                Players.player_id,
                Players.nationality,
                Players.city,
                Players.number,
                Players.dominant_foot,
                Players.primary_position,
                Players.secondary_position,
                Players.height,
                PlayerGameStats.goals,
                PlayerGameStats.minutes_played
            )
            .join(Players, Users.user_id == Players.user_id)
            .join(PlayerGameStats, Players.player_id == PlayerGameStats.player_id)
            .filter(Players.player_id == selected_player_id)
            .first()
        )

        if not result:
            st.info("No se encontraron datos para mostrar.")
            return

        # Desempaquetar resultados
        (
            user_id, first_name, last_name, birth_date, gender, photo_url, phone,
            player_id, nationality, city, number, dominant_foot, primary_position,
            secondary_position, height, goals, minutes_played
        ) = result

        # Foto
        if photo_url:
            st.image(photo_url, width=300)
        else:
            st.info("No se encontró imagen para este jugador.")

        # Cálculos
        age = datetime.today().year - birth_date.year - (
            (datetime.today().month, datetime.today().day) < (birth_date.month, birth_date.day)
        )
        goals_90 = (goals / minutes_played) * 90 if minutes_played else 0

        # GENERAL INFO
        general_fields = {
            "Last Name": last_name,
            "First Name": first_name,
            "Birth Date": birth_date,
            "Age": age,
            "Gender": gender,
            "Nationality": nationality,
            "City": city,
            "Contact Phone": phone
        }

        # PLAYER PROFILE & STATS
        profile_fields = {
            "Number": number,
            "Dominant Foot": dominant_foot,
            "Primary Position": primary_position,
            "Secondary Position": secondary_position,
            "Height": height,
            "Minutes Played": minutes_played,
            "Goals": goals,
            "Goals/90": round(goals_90, 2)
        }

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("GENERAL INFO", divider="red")
            st.table(general_fields)
        with col2:
            st.subheader("PLAYER PROFILE & STATS", divider="red")
            st.table(profile_fields)

        # Puedes agregar más secciones aquí (videos, métricas, documentos, etc.)

def main():
    Setup_page()
    Show_Player_Info()

if __name__ == "__main__":
    main()
