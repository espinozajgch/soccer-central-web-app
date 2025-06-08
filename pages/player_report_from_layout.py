import streamlit as st
from utils import login
from datetime import datetime
from utils.pdf_generator import generate_player_report
import random
import plotly.express as px
import base64
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from models import Users, Players
from db import engine  # Asegúrate de tener tu engine SQLAlchemy configurado
import plotly.graph_objects as go
import random

login.generarLogin()

if "usuario" not in st.session_state:
    st.stop()

def calculate_age(birth_date):
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_goals_per_90(goals, minutes_played):
    return (goals / minutes_played) * 90 if minutes_played else 0

def radar_chart():
    categories = ['On Ball', 'Intelligence', 'Shot', 'Defensive', 'Aerial', 'Physical']
    values = [random.randint(60, 95) for _ in categories]
    # Cerramos el radar uniendo el primer punto
    values.append(values[0])
    categories.append(categories[0])

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Player Performance',
                line_color='lime'
            )
        ]
    )

    

    return fig

def Show_Player_Info():
    st.header("360° PLAYER DATA", divider="gray")

    with Session(engine) as session:
        users = session.query(Users).filter(Users.role_id == 4).order_by(Users.last_name).all()
        user_options = [f"{u.first_name} {u.last_name}" for u in users]
        selected_name = st.selectbox("Choose Player", user_options)

        selected_user = next(u for u in users if f"{u.first_name} {u.last_name}" == selected_name)
        player = selected_user.players[0] if selected_user.players else None

        # Foto
        photo_url = selected_user.photo_url or "https://via.placeholder.com/200x250?text=No+Photo"
        st.image(photo_url, width=200)

        # Datos personales
        birth_date = selected_user.birth_date
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("GENERAL INFO", divider="red")
            st.markdown(f"""
            - **Last name**: {selected_user.last_name}
            - **First name**: {selected_user.first_name}
            - **Birth date**: {birth_date}
            - **Gender**: {selected_user.gender}
            - **Nationality**: {selected_user.country}
            - **Phone**: {selected_user.phone}
            - **Age**: {calculate_age(birth_date)}
            """)

        # Perfil (simulado o real si hay)
        with col2:
            st.subheader("PLAYER PROFILE & STATS", divider="red")
            number = player.number if player else random.randint(1, 99)
            dominant_foot = player.dominant_foot if player else "Right"
            primary_position = player.primary_position if player else "Midfielder"
            secondary_position = player.secondary_position if player else "Winger"
            height = player.height if player else random.randint(165, 190)
            games_played = random.randint(10, 30)
            minutes_played = random.randint(800, 2700)
            starter_games = random.randint(5, 20)
            goals = random.randint(1, 10)
            goals_per_90 = calculate_goals_per_90(goals, minutes_played)

            st.markdown(f"""
            - **Name**: {selected_name}
            - **Number**: {number}
            - **Dominant foot**: {dominant_foot}
            - **Primary position**: {primary_position}
            - **Secondary position**: {secondary_position}
            - **Height**: {height} cm
            - **Games Played**: {games_played}
            - **Total minutes played**: {minutes_played}
            - **Starter games**: {starter_games}
            - **Goals**: {goals}
            - **Goals per 90 minutes**: {goals_per_90:.2f}
            """)

        # Radar y habilidades
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("PLAYER PERFORMANCE", divider="green")
            st.plotly_chart(radar_chart(), use_container_width=True)

        with col4:
            st.subheader("ANALYSIS BY SKILLS", divider="blue")
            skills = [
                ("On Ball", "Displays exceptional ball control and agility."),
                ("Intelligence", "Outstanding vision and play anticipation."),
                ("Shot", "Powerful and accurate shooting."),
                ("Defensive", "Great marking and interception."),
                ("Aerial", "Strong in aerial duels."),
                ("Physical", "Superior strength and endurance.")
            ]
            for skill, desc in skills:
                st.markdown(f"- **{skill}**: {desc}")

        # Datos para el PDF
        player_data = {
            "first_name": selected_user.first_name,
            "last_name": selected_user.last_name,
            "birth_date": selected_user.birth_date,
            "nationality": selected_user.country,
            "primary_position": primary_position,
            "secondary_position": secondary_position,
            "number": number,
            "dominant_foot": dominant_foot,
            "height": height,
            "education_level": player.education_level if player else "High School",
            "school_name": player.school_name if player else "Soccer Central SA",
            "photo_url": photo_url,
            "notes": player.notes if player else "",
            "player_activity_history": player.player_activity_history if player else ""
        }

        if st.button(" Download Player Report"):
            with st.spinner("⏳ Generating PDF... Please wait"):
                pdf_buffer = generate_player_report(
                    player_data=player_data,
                    player_teams=[], player_games=[], player_metrics=[],
                    player_evaluations=[], player_videos=[], player_documents=[]
                )

            pdf_bytes = pdf_buffer.getvalue()
            b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_filename = f"player_report_{player_data['last_name']}.pdf"

            st.success("Report generated!")
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer.getvalue(),
                file_name=f"player_report_{player_data['last_name']}.pdf",
                mime="application/pdf"
            )

def main():
    Show_Player_Info()

if __name__ == "__main__":
    main()
