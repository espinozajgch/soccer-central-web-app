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

def connect_to_db():
    try:
        return st.connection('mysql', type='sql')
    except Exception as e:
        st.error("Error connecting to database:")
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
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False
    )
    return fig

def Setup_page():
    login.generarLogin()
    
    # Add logo to sidebar
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)
    
    # Color pickers with containers for better styling
    with st.sidebar.container():
        st.sidebar.title("Theme Customization")
        main_bg_color = st.color_picker("Principal Panel Color", "#EDF4F5")
        sidebar_bg_color = st.color_picker("Sidebar Panel Color", "#D0DEE2")

def Show_Player_Info():
    dbconn = connect_to_db()
    
    # Main header with container
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("360° PLAYER DATA")
            st.divider()

    # Player selection with improved UI
    df_users = dbconn.query("SELECT * FROM users WHERE role_id = 4 ORDER BY last_name", ttl=3600)
    df_users["full_name"] = df_users["first_name"] + " " + df_users["last_name"]
    
    with st.container():
        selected_name = st.selectbox(
            "Select Player",
            df_users["full_name"],
            index=0,
            help="Choose a player to view their detailed report"
        )
    
    selected_user = df_users[df_users["full_name"] == selected_name].iloc[0]
    
    # Player overview section
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Photo with expander for details
            photo_url = selected_user["photo_url"] or "https://via.placeholder.com/200x250?text=No+Photo"
            st.image(photo_url, width=200, caption=selected_name)
            
        with col2:
            # Key metrics in a clean layout
            st.subheader("Key Statistics")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Age", calculate_age(selected_user["birth_date"]))
            with metric_col2:
                st.metric("Position", "Midfielder")
            with metric_col3:
                st.metric("Games", random.randint(10, 30))

    # Detailed information in tabs
    tab1, tab2, tab3 = st.tabs(["Personal Info", "Performance", "Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("General Information")
            personal_info = {
                "Last name": selected_user["last_name"],
                "First name": selected_user["first_name"],
                "Birth date": selected_user["birth_date"],
                "Gender": selected_user["gender"],
                "Nationality": selected_user["country"],
                "Phone": selected_user["phone"]
            }
            for key, value in personal_info.items():
                st.text_input(key, value, disabled=True)
                
        with col2:
            st.subheader("Player Profile")
            profile_info = {
                "Position": "Midfielder",
                "Number": random.randint(1, 99),
                "Height": f"{random.randint(165, 190)} cm",
                "Dominant Foot": "Right"
            }
            for key, value in profile_info.items():
                st.text_input(key, value, disabled=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(radar_chart(), use_container_width=True)
        with col2:
            st.subheader("Performance Metrics")
            metrics = {
                "Games Played": random.randint(10, 30),
                "Minutes": random.randint(800, 2700),
                "Goals": random.randint(1, 10),
                "Assists": random.randint(1, 8)
            }
            for key, value in metrics.items():
                st.metric(key, value)
    
    with tab3:
        st.subheader("Skill Analysis")
        skills_data = {
            "Skill": ["On Ball", "Intelligence", "Shot", "Defensive", "Aerial", "Physical"],
            "Rating": [random.randint(60, 95) for _ in range(6)],
            "Description": [
                "Exceptional ball control and dribbling",
                "Outstanding vision and anticipation",
                "Powerful and accurate shooting",
                "Solid defensive positioning",
                "Strong in aerial duels",
                "Superior physical presence"
            ]
        }
        df_skills = pd.DataFrame(skills_data)
        st.dataframe(
            df_skills,
            column_config={
                "Skill": "Attribute",
                "Rating": st.column_config.ProgressColumn(
                    "Rating",
                    help="Player rating out of 100",
                    format="%d",
                    min_value=0,
                    max_value=100,
                ),
                "Description": "Analysis"
            },
            hide_index=True,
            use_container_width=True
        )

    # PDF Generation section
    st.divider()
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Generate PDF Report", type="primary", use_container_width=True):
                with st.spinner("⏳ Generating comprehensive player report..."):
                    player_data = {
                        "first_name": selected_user["first_name"],
                        "last_name": selected_user["last_name"],
                        "birth_date": selected_user["birth_date"],
                        "nationality": selected_user["country"],
                        "primary_position": "Midfielder",
                        "secondary_position": "Winger",
                        "number": random.randint(1, 99),
                        "dominant_foot": "Right",
                        "height": random.randint(165, 190),
                        "education_level": "High School",
                        "school_name": "Soccer Central SA",
                        "photo_url": photo_url,
                        "notes": "",
                        "player_activity_history": ""
                    }
                    
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
                    
                    st.success("Report generated successfully!")
                    st.download_button(
                        label="Download Report",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )

def main():
    Setup_page()
    Show_Player_Info()

if __name__ == "__main__":
    main()