import streamlit as st
from utils import login
import pandas as pd
import numpy as np
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime
from sc_app.queries import player_360
from utils.pdf_generator import generate_player_report
import random
import plotly.express as px
import base64


def connect_to_db():
    try:
        return st.connection('mysql', type='sql')
    except Exception as e:
        st.error("Error al conectar con la base de datos:")
        st.error(e)
    return None


def calculate_age(birth_date):
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def calculate_goals_per_90(goals, minutes_played):
    return (goals / minutes_played) * 90 if minutes_played else 0


def Setup_page():
    login.generarLogin()
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)

    main_bg_color = st.sidebar.color_picker("**Choose Background Color for Principal Panel**", "#EDF4F5")
    sidebar_bg_color = st.sidebar.color_picker("**Choose Background Color for Sidebar Panel**", "#D0DEE2")

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-color: {main_bg_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def radar_chart():
    dfx = pd.DataFrame(dict(
        r=[random.randint(0, 22) for _ in range(6)],
        theta=['On Ball', 'Intelligence', 'Shot', 'Defensive', 'Aerial', 'Physical']
    ))
    fig = px.line_polar(dfx, r='r', theta='theta', line_close=True, template="plotly_dark")
    return fig


def Show_Player_Info():
    dbconn = connect_to_db()
    st.header("360° PLAYER DATA", divider="gray")

    df_plyid = dbconn.query("SELECT player_id FROM players", ttl=3600)
    player_ids = df_plyid["player_id"].tolist()
    selected_player_id = st.sidebar.selectbox("Choose Player", player_ids)

    try:
        df = dbconn.query(player_360, params={"player_id": selected_player_id}, ttl=3600)
        df = df.iloc[[0]]
    except Exception as e:
        st.error(f"Error durante la consulta: {e}")
        return

    # Acceso a datos individuales
    player_row = df.iloc[0]
    birth_date = player_row["birth_date"]

    # Datos personales
    df_personal = pd.DataFrame({
        "last_name": [player_row["last_name"]],
        "first_name": [player_row["first_name"]],
        "birth_date": [birth_date],
        "gender": [player_row["gender"]],
        "nationality": [player_row["nationality"]],
        "city": [player_row["city"]],
        "phone": [player_row["phone"]],
        "age": [calculate_age(birth_date)]
    })

    # Imagen de ejemplo fija
    photo_url = "https://media.gettyimages.com/id/1365815844/es/foto/mexico-city-mexico-argentina-captain-diego-maradona.jpg?s=612x612"
    st.image(photo_url, width=200)

    # Datos de perfil
    df_profile = pd.DataFrame({
        "name": [player_row["name"]],
        "number": [player_row["number"]],
        "dominant_foot": [player_row["dominant_foot"]],
        "primary_position": [player_row["primary_position"]],
        "secondary_position": [player_row["secondary_position"]],
        "height": [player_row["height"]],
        "games_played": [player_row["games_played"]],
        "total_minutes_played": [player_row["total_minutes_played"]],
        "starter_games": [player_row["starter_games"]],
        "goals": [player_row["goals"]],
    })

    df_profile["goals_per_90"] = calculate_goals_per_90(
        player_row["goals"], player_row["total_minutes_played"]
    )

    # Reformateo para tablas Streamlit
    df_personal_long = pd.melt(df_personal, var_name="Personal Info", value_name="Value").astype(str)
    df_profile_long = pd.melt(df_profile, var_name="Profile", value_name="Value").astype(str)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("GENERAL INFO", divider="red")
        st.dataframe(df_personal_long, hide_index=True)
    with col2:
        st.subheader("PLAYER PROFILE & STATS", divider="red")
        st.dataframe(df_profile_long, hide_index=True, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("PLAYER PERFORMANCE", divider="green")
        st.plotly_chart(radar_chart(), use_container_width=True)
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

    # Preparar PDF
    empty_df = pd.DataFrame()
    player_data = {
        "first_name": player_row["first_name"],
        "last_name": player_row["last_name"],
        "birth_date": player_row["birth_date"],
        "nationality": player_row["nationality"],
        "primary_position": player_row["primary_position"],
        "secondary_position": player_row["secondary_position"],
        "number": player_row["number"],
        "dominant_foot": player_row["dominant_foot"],
        "height": player_row["height"],
        "education_level": "High School",
        "school_name": "Soccer Central SA",
        "photo_url": photo_url,
        "notes": player_row.get("notes", ""),
        "player_activity_history": player_row.get("player_activity_history", "")
    }

    if st.button(" Download Player Report"):
        with st.spinner("⏳ Generating PDF... Please wait"):
            pdf_buffer = generate_player_report(
                player_data=player_data,
                player_teams=empty_df,
                player_games=empty_df,
                player_metrics=empty_df,
                player_evaluations=empty_df,
                player_videos=empty_df,
                player_documents=empty_df
            )

        pdf_bytes = pdf_buffer.getvalue()
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_filename = f"player_report_{player_data['last_name']}.pdf"

        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Click here if download doesn\'t start</a>'
        st.success("Report generated!")

        js = f"""
        <script>
            const link = document.createElement('a');
            link.href = 'data:application/pdf;base64,{b64_pdf}';
            link.download = '{pdf_filename}';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        </script>
        """
        st.components.v1.html(js, height=0)
        st.markdown(href, unsafe_allow_html=True)


def main():
    Setup_page()
    Show_Player_Info()


if __name__ == "__main__":
    main()
