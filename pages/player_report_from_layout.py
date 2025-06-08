import streamlit as st
from utils import login
import pandas as pd
import numpy as np
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime
from utils.pdf_generator import generate_player_report
import random
import plotly.express as px
import base64

login.generarLogin()

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

def radar_chart():
    dfx = pd.DataFrame(dict(
        r=[random.randint(60, 95) for _ in range(6)],
        theta=['On Ball', 'Intelligence', 'Shot', 'Defensive', 'Aerial', 'Physical']
    ))
    fig = px.line_polar(dfx, r='r', theta='theta', line_close=True, template="plotly_dark")
    return fig


def Show_Player_Info():
    dbconn = connect_to_db()
    st.header("360° PLAYER DATA", divider="gray")

    df_users = dbconn.query("SELECT * FROM users WHERE role_id = 4 ORDER BY last_name", ttl=3600)
    df_users["full_name"] = df_users["first_name"] + " " + df_users["last_name"]

    selected_name = st.selectbox("Choose Player", df_users["full_name"])
    selected_user = df_users[df_users["full_name"] == selected_name].iloc[0]

    # Datos personales
    birth_date = selected_user["birth_date"]
    df_personal = pd.DataFrame({
        "Last name": [selected_user["last_name"]],
        "First name": [selected_user["first_name"]],
        "Birth date": [birth_date],
        "Gender": [selected_user["gender"]],
        "Nationality": [selected_user["country"]],
        "Phone": [selected_user["phone"]],
        "Age": [calculate_age(birth_date)]
    })

    # Foto
    photo_url = selected_user["photo_url"] or "https://via.placeholder.com/200x250?text=No+Photo"
    st.image(photo_url, width=200)

    # Perfil simulado
    df_profile = pd.DataFrame({
        "Name": [selected_user["full_name"]],
        "Number": [random.randint(1, 99)],
        "Dominant foot": ["Right"],
        "Primary position": ["Midfielder"],
        "Secondary position": ["Winger"],
        "Height": [random.randint(165, 190)],
        "Games Played": [random.randint(10, 30)],
        "Total minutes played": [random.randint(800, 2700)],
        "Starter games": [random.randint(5, 20)],
        "Goals": [random.randint(1, 10)],
    })

    df_profile["goals_per_90"] = calculate_goals_per_90(
        df_profile["Goals"][0], df_profile["Total minutes played"][0]
    )

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

    player_data = {
        "first_name": selected_user["first_name"],
        "last_name": selected_user["last_name"],
        "birth_date": selected_user["birth_date"],
        "nationality": selected_user["country"],
        "primary_position": "Midfielder",
        "secondary_position": "Winger",
        "number": df_profile["Number"][0],
        "dominant_foot": "Right",
        "height": df_profile["Height"][0],
        "education_level": "High School",
        "school_name": "Soccer Central SA",
        "photo_url": photo_url,
        "notes": "",
        "player_activity_history": ""
    }

    if st.button(" Download Player Report"):
        with st.spinner("⏳ Generating PDF... Please wait"):
            pdf_buffer = generate_player_report(
                player_data=player_data,
                player_teams=pd.DataFrame(),
                player_games=pd.DataFrame(),
                player_metrics=pd.DataFrame(),
                player_evaluations=pd.DataFrame(),
                player_videos=pd.DataFrame(),
                player_documents=pd.DataFrame()
            )

        pdf_bytes = pdf_buffer.getvalue()
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_filename = f"player_report_{player_data['last_name']}.pdf"

        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Click here if download doesn\'t start</a>'
        st.success("Report generated!")
        st.components.v1.html(f"""
            <script>
                const link = document.createElement('a');
                link.href = 'data:application/pdf;base64,{b64_pdf}';
                link.download = '{pdf_filename}';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            </script>
        """, height=0)
        st.markdown(href, unsafe_allow_html=True)

def main():
    Show_Player_Info()

if __name__ == "__main__":
    main()
