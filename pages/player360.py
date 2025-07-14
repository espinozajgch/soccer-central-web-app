import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.models import Users, PlayerTeams, Metrics, PlayerEvaluations, Teams
from db.db import engine 
from datetime import datetime
from utils.pdf_generator import generate_player_report
import random
import plotly.graph_objects as go
from utils import util
from utils.util import get_current_user


util.setup_page("Player 360")

# LOGIN + MENU
util.login_if_needed()

st.header(":blue[Players] Dashboard", divider=True)

# Rayner colours
BRAND_COLORS =util.get_brand_colors_list()

def calculate_age(birth_date):
    if not birth_date:
        return None
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def create_enhanced_radar_chart():
    categories = ['Technical', 'Physical', 'Mental', 'Tactical', 'Leadership', 'Consistency']
    values = [random.randint(60, 95) for _ in categories]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Player Performance',
        line=dict(color=BRAND_COLORS[2], width=3),
        fillcolor=f'rgba(92, 116, 180, 0.3)',
        marker=dict(size=8, color=BRAND_COLORS[0])
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color=BRAND_COLORS[3]),
                gridcolor=BRAND_COLORS[6]
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=BRAND_COLORS[3]),
                linecolor=BRAND_COLORS[6]
            )
        ),
        showlegend=False,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=BRAND_COLORS[3])
    )
    
    return fig

def create_performance_trend_chart():
    months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May']
    performance = [random.randint(70, 95) for _ in months]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months, y=performance,
        mode='lines+markers',
        name='Performance Rating',
        line=dict(color=BRAND_COLORS[0], width=3),
        marker=dict(size=8, color=BRAND_COLORS[0])
    ))
    
    fig.update_layout(
        title=dict(text="Season Performance Trend", font=dict(size=16, color=BRAND_COLORS[3])),
        xaxis_title="Month",
        yaxis_title="Performance Rating",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=BRAND_COLORS[3]),
        hovermode='x unified'
    )
    
    return fig

def show_player_info():
    with Session(engine) as session:
        users = session.query(Users).filter(Users.role_id == 4).order_by(Users.last_name).all()
        user_options = [f"{u.first_name} {u.last_name}" for u in users]
        current_user = get_current_user(session)

        #  SOLO muestra selectbox si NO es jugador
        if current_user.role_id != 4:
            users = session.query(Users).filter(Users.role_id == 4).order_by(Users.last_name).all()
            user_options = [f"{u.first_name} {u.last_name}" for u in users]
            selected_name = st.selectbox(
                "Select Player for Analysis",
                user_options,
                help="Choose a player to view detailed analytics and performance metrics",
                key="select_player_360"
            )
            selected_user = next(u for u in users if f"{u.first_name} {u.last_name}" == selected_name)
        else:
            # Jugador: solo ve su propia información, sin selectbox
            selected_user = current_user

        player = selected_user.players[0] if selected_user.players else None

        # Cargar datos para el pdf
        player_teams_df = pd.read_sql(
            session.query(PlayerTeams).filter_by(player_id=player.player_id).statement,
            session.bind
        )
        player_metrics_df = pd.read_sql(
            session.query(Metrics).filter_by(player_id=player.player_id).statement,
            session.bind
        )
        player_evaluations_df = pd.read_sql(
            session.query(PlayerEvaluations).filter_by(player_id=player.player_id).statement,
            session.bind
        )
        teams_df = pd.read_sql(
            session.query(Teams).statement,
             session.bind
        )
        # fin logica

        st.divider()

        # Redesigned Header Section
        photo_url = getattr(selected_user, "photo_url", None) or "https://cdn-icons-png.flaticon.com/512/149/149071.png"
        birth_date = pd.to_datetime(selected_user.birth_date, errors="coerce")
        age = calculate_age(birth_date) if pd.notnull(birth_date) else "Not Available"

        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(photo_url, width=160)
        with col2:
            st.markdown(f"### **{selected_user.first_name.upper()} {selected_user.last_name.upper()}**")
            st.markdown(f"""
                **ID:** `{getattr(player, 'player_id', 'Not Available')}` |
                **Nationality:** `{getattr(player, 'nationality', selected_user.country) or 'Not Available'}`
            """)
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            metric_col1.metric("Category", getattr(player, "grade_level", "Check in"))
            metric_col2.metric("Position", getattr(player, "primary_position", "Not available"))
            metric_col3.metric("Birth Date", birth_date.strftime('%d/%m/%Y') if pd.notnull(birth_date) else "Not Available")
            metric_col4.metric("Age", f"{age} years" if age != "Not Available" else "Not Available")

        st.divider()

        # New Analytics Tabs
        analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs([
            "Anthropometry",
            "Metrics",
            "Evaluations"
        ])

        with analytics_tab1:
            st.subheader("Anthropometric Evaluation")
            col_a, col_b, col_c = st.columns(3)
            height = getattr(player, "height", None)
            weight = getattr(player, "weight", None)
            with col_a:
                st.metric("Height (m)", f"{float(player.height) / 100:.2f}" if height else "Not Available", delta=f"{height:.2f}" if height else None)
            with col_b:
                st.metric("Weight (kg)", f"{weight:.2f}" if weight else "Not Available", delta=f"{weight:.2f}" if weight else None)

        with analytics_tab2:
            st.subheader("Player Metrics")
            if player:
                metrics = player.metrics
                if metrics:
                    for m in metrics:
                        with st.expander(f"Metric: {m.drill_name or 'Unnamed'} on {m.training_date.strftime('%Y-%m-%d') if m.training_date else 'N/A'}", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            col1.write(f"**Drill:** {m.drill_name}")
                            col2.write(f"**Level:** {m.level}")
                            col3.write(f"**Goal:** {m.goal}")

                            col4, col5, col6 = st.columns(3)
                            col4.metric("Hits", m.hits)
                            col5.metric("Misses", m.misses)
                            col6.metric("Drops", m.drops)

                            col7, col8, col9 = st.columns(3)
                            col7.metric("Correct", m.correct)
                            col8.metric("Wrong", m.wrong)
                            col9.metric("Distractions", m.distraction)

                            st.metric("Avg Reaction Time", f"{m.avg_reaction_time}s" if m.avg_reaction_time else "N/A")
                            if m.notes:
                                st.text_area("Notes", m.notes, disabled=True)
                else:
                    st.info("No metrics found for this player.")
            else:
                st.warning("No player selected.")

        with analytics_tab3:
            st.subheader("Player Evaluations")
            if player:
                evaluations = player.player_evaluations
                if evaluations:
                    for e in evaluations:
                        with st.expander(f"Evaluation: {e.metric_name or 'Unnamed'} on {e.evaluation_date.strftime('%Y-%m-%d') if e.evaluation_date else 'N/A'}", expanded=False):
                            col1, col2 = st.columns(2)
                            col1.write(f"**Category:** {e.category}")
                            col2.write(f"**Metric:** {e.metric_name}")

                            st.metric("Value", e.value)

                            if e.notes:
                                st.text_area("Notes", e.notes, disabled=True)
                else:
                    st.info("No evaluations found for this player.")
            else:
                st.warning("No player selected.")
        # Enhanced tabbed interface
        tab1, tab2, tab3, tab4 = st.tabs([
            "Player Profile", 
            "Performance Analytics", 
            "Detailed Information",
            "Reports & Documents"
        ])
        
        with tab1:
            profile_col1, profile_col2 = st.columns(2)
            
            with profile_col1:
                st.subheader("Personal Information")
                
                # Enhanced personal info display using database fields
                personal_data = [
                    ("Full Name", f"{selected_user.first_name} {selected_user.last_name}"),
                    ("Birth Date", str(selected_user.birth_date)),
                    ("Age", f"{age} years"),
                    ("Gender", selected_user.gender),
                    ("Country", selected_user.country),
                    ("Phone", getattr(player, "phone", selected_user.phone) if player else selected_user.phone)
                ]
                
                for label, value in personal_data:
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.write(f"**{label}:**")
                    with col_b:
                        st.info(value)
                        
                st.subheader("Teams")

                if player and player.player_teams:
                    for t in player.player_teams:
                        team_name = t.team.name if t.team and t.team.name else "Unknown"
                        start = t.start_date.strftime('%d/%m/%Y') if t.start_date else "N/A"
                        end = t.end_date.strftime('%d/%m/%Y') if t.end_date else "Present"

                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.write("**Team:**")
                        with col_b:
                            st.info(team_name)

                        col_c, col_d = st.columns([1, 2])
                        with col_c:
                            st.write("**From:**")
                        with col_d:
                            st.success(start)

                        col_e, col_f = st.columns([1, 2])
                        with col_e:
                            st.write("**To:**")
                        with col_f:
                            st.success(end)

                        st.markdown("---")
                else:
                    st.info("No team history available.")


            with profile_col2:
                st.subheader("Player Details")
                
                # Enhanced player profile using actual database fields
                player_data = [
                    ("Jersey Number", str(getattr(player, "number", "Not assigned")) if player else "Not assigned"),
                    ("Primary Position", getattr(player, "primary_position", "Not specified") if player else "Not specified"),
                    ("Secondary Position", getattr(player, "secondary_position", "Not specified") if player else "Not specified"),
                    ("Dominant Foot", getattr(player, "dominant_foot", "Not specified") if player else "Not specified"),
                    ("Height", f"{float(player.height) / 100:.2f} m / {float(player.height) * 0.393701:.1f} in" if player and player.height else "Not specified"),
                    ("Training Location", getattr(player, "training_location", "Not specified") if player else "Not specified")
                ]
                
                for label, value in player_data:
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.write(f"**{label}:**")
                    with col_b:
                        st.success(value)

               
        
        with tab2:
            st.subheader("Performance Analytics Dashboard")
            
            # Performance charts section - commented until we have right values
            #chart_col1, chart_col2 = st.columns(2)
            
           #with chart_col1:
                #st.plotly_chart(create_enhanced_radar_chart(), use_container_width=True)
            
            #with chart_col2:
                #st.plotly_chart(create_performance_trend_chart(), use_container_width=True)
            
            # Additional metrics using database fields
            with st.expander("Player Statistics", expanded=False):
                adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
                
                with adv_col1:
                    st.metric("Grade Level", getattr(player, "grade_level", "Not specified") if player else "Not specified")
                    st.metric("Shirt Size", getattr(player, "shirt_size", "Not specified") if player else "Not specified")
                
                with adv_col2:
                    st.metric("Short Size", getattr(player, "short_size", "Not specified") if player else "Not specified")
                    birth_cert = getattr(player, "birth_certificate_on_file", False) if player else False
                    st.metric("Birth Certificate", "Yes" if birth_cert else "No")
                
                with adv_col3:
                    birthdate_verified = getattr(player, "birthdate_verified", False) if player else False
                    st.metric("Birthdate Verified", "Yes" if birthdate_verified else "No")
                    country_birth = getattr(player, "country_of_birth", "Not specified") if player else "Not specified"
                    st.metric("Country of Birth", country_birth)
                
                with adv_col4:
                    country_citizenship = getattr(player, "country_of_citizenship", "Not specified") if player else "Not specified"
                    st.metric("Citizenship", country_citizenship)
                    city = getattr(player, "city", "Not specified") if player else "Not specified"
                    st.metric("City", city)
        
        with tab3:
            st.subheader("Comprehensive Player Information")
            
            # Academic and Educational Information
            st.subheader("Academic Information")
            
            academic_col1, academic_col2 = st.columns(2)
            
            with academic_col1:
                graduation_date = getattr(player, "graduation_date", None) if player else None
                st.text_input("School Name", getattr(player, "school_name", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Education Level", getattr(player, "education_level", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Grade Level", str(getattr(player, "grade_level", "Not specified")) if player else "Not specified", disabled=True)
                st.text_input("Graduation Date", str(graduation_date) if graduation_date else "Not specified", disabled=True)
            
            with academic_col2:
                st.text_input("Last Team", getattr(player, "last_team", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Athlete Number", str(getattr(player, "athlete_number", "Not specified")) if player else "Not specified", disabled=True)
                registration_date = getattr(player, "registration_date", None) if player else None
                st.text_input("Registration Date", str(registration_date) if registration_date else "Not specified", disabled=True)
                sanctioned = getattr(player, "sanctioned_outside_us", False) if player else False
                st.text_input("Sanctioned Outside US", "Yes" if sanctioned else "No", disabled=True)
            
            st.divider()
            
            # Medical and Insurance Information
            st.subheader("Medical & Insurance Information")
            
            medical_col1, medical_col2 = st.columns(2)
            
            with medical_col1:
                st.text_input("Insurance Company", getattr(player, "insurance_company", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Insurance Policy Number", getattr(player, "insurance_policy_number", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Insurance Group Number", getattr(player, "insurance_group_number", "Not specified") if player else "Not specified", disabled=True)
            
            with medical_col2:
                st.text_input("Physician Name", getattr(player, "physician_name", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Physician Phone", getattr(player, "physician_phone", "Not specified") if player else "Not specified", disabled=True)
                st.text_input("Social Security Number", getattr(player, "social_security_number", "Protected") if player else "Not specified", disabled=True)
            
            # Health Notes
            health_notes = getattr(player, "health_notes", "No health notes available") if player else "No health notes available"
            st.text_area("Health Notes", health_notes, disabled=True, height=100)
            
            st.divider()
            
            # Activity History and Notes
            st.subheader("Activity History & Notes")
            
            activity_history = getattr(player, "player_activity_history", "No activity history available") if player else "No activity history available"
            st.text_area("Player Activity History", activity_history, disabled=True, height=150)
            
            notes = getattr(player, "notes", "No additional notes") if player else "No additional notes"
            st.text_area("Additional Notes", notes, disabled=True, height=100)

            
        
        with tab4:
            st.subheader("Reports & Documentation Center")
            
            # Report generation section
            report_col1, report_col2 = st.columns(2)
            
            with report_col1:
                with st.container():
                    st.write("### Complete Player Report")
                    st.write("Generate comprehensive PDF with all analytics, statistics, and performance insights.")
                    
                    if st.button("Generate Full Report", type="primary", use_container_width=True):
                        with st.spinner("Creating comprehensive player analysis..."):
                            player_data = {
                                "first_name": selected_user.first_name,
                                "last_name": selected_user.last_name,
                                "player_id": getattr(player, "player_id", "N/A") if player else "N/A",
                                "birth_date": selected_user.birth_date,
                                "nationality": getattr(player, "nationality", selected_user.country) if player else selected_user.country,
                                "primary_position": getattr(player, "primary_position", "Not specified") if player else "Not specified",
                                "secondary_position": getattr(player, "secondary_position", "Not specified") if player else "Not specified",
                                "number": getattr(player, "number", "Not assigned") if player else "Not assigned",
                                "dominant_foot": getattr(player, "dominant_foot", "Not specified") if player else "Not specified",
                                "height": getattr(player, "height", "Not specified") if player else "Not specified",
                                "education_level": getattr(player, "education_level", "Not specified") if player else "Not specified",
                                "school_name": getattr(player, "school_name", "Soccer Central SA") if player else "Soccer Central SA",
                                "photo_url": photo_url,
                                "notes": getattr(player, "notes", "") if player else "",
                                "player_activity_history": getattr(player, "player_activity_history", "") if player else ""
                            }

                            # Obtenemos los datos para la tabla del pdf

                            player_assessment_query = text("""
                            SELECT category, item, value 
                            FROM player_assessments 
                            WHERE player_id = :player_id
                            """)
                            player_assessment_df = pd.read_sql(player_assessment_query, session.bind, params={"player_id": player.player_id})
                            
                            pdf_bytes = generate_player_report(
                                        player_data=player_data,
                                        player_teams=player_teams_df,
                                        player_games=pd.DataFrame(),  # pendiente
                                        player_metrics=player_metrics_df,
                                        player_evaluations=player_evaluations_df,
                                        player_videos=pd.DataFrame(),  # pendiente
                                        player_documents=pd.DataFrame(),  # pendiente
                                        teams_df=teams_df, # para el nombre del equipo en el pdf, no es lo mismo que player_teams
                                        player_assessments=player_assessment_df # para la tabla del pdf
                                    )
                            
                            st.success("Report generated successfully!")
                            st.download_button(
                                label="Download Complete Report",
                                data=pdf_bytes,
                                file_name=f"complete_report_{player_data['last_name']}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
            
            with report_col2:
                with st.container():
                    st.write("### Documentation Status")
                    st.write("Track important documentation and verification status.")
                    
                    # Documentation status using database fields
                    doc_status = []
                    if player:
                        doc_status = [
                            ("Birth Certificate", "Complete" if getattr(player, "birth_certificate_on_file", False) else "Pending"),
                            ("Birthdate Verification", "Verified" if getattr(player, "birthdate_verified", False) else "Pending"),
                            ("Insurance Information", "Complete" if getattr(player, "insurance_company", None) else "Pending"),
                            ("Medical Information", "Complete" if getattr(player, "physician_name", None) else "Pending")
                        ]
                    else:
                        doc_status = [
                            ("Birth Certificate", "No player record"),
                            ("Birthdate Verification", "No player record"),
                            ("Insurance Information", "No player record"),
                            ("Medical Information", "No player record")
                        ]
                    
                    for doc, status in doc_status:
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(doc)
                        with col_b:
                            if status == "Complete" or status == "Verified":
                                st.success(status)
                            elif status == "Pending":
                                st.warning(status)
                            else:
                                st.error(status)
            
            # Recent activity section using database fields
            with st.expander("Player Information Summary", expanded=False):
                if player:
                    summary_data = {
                        "Field": [
                            "Player ID", "User ID", "Number", "School Name", "Primary Position",
                            "Secondary Position", "Training Location", "Grade Level", "Shirt Size",
                            "Short Size", "Country of Birth", "Country of Citizenship", "City",
                            "Education Level", "Last Team", "Dominant Foot", "Height", "Athlete Number"
                        ],
                        "Value": [
                            str(getattr(player, "player_id", "N/A")),
                            str(getattr(player, "user_id", "N/A")),
                            str(getattr(player, "number", "N/A")),
                            getattr(player, "school_name", "Not specified"),
                            getattr(player, "primary_position", "Not specified"),
                            getattr(player, "secondary_position", "Not specified"),
                            getattr(player, "training_location", "Not specified"),
                            str(getattr(player, "grade_level", "Not specified")),
                            getattr(player, "shirt_size", "Not specified"),
                            getattr(player, "short_size", "Not specified"),
                            getattr(player, "country_of_birth", "Not specified"),
                            getattr(player, "country_of_citizenship", "Not specified"),
                            getattr(player, "city", "Not specified"),
                            getattr(player, "education_level", "Not specified"),
                            getattr(player, "last_team", "Not specified"),
                            getattr(player, "dominant_foot", "Not specified"),
                            str(getattr(player, "height", "Not specified")),
                            str(getattr(player, "athlete_number", "Not specified"))
                        ]
                    }
                    
                    df_summary = pd.DataFrame(summary_data)
                    st.dataframe(
                        df_summary,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.warning("No player record found for this user.")

def main():
    show_player_info()

if __name__ == "__main__":
    main()