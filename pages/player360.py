import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db.models import Users
from db.db import engine 
from datetime import datetime
from utils.pdf_generator import generate_player_report
import random
import plotly.graph_objects as go
from utils import util

util.setup_page("Player 360")

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
                
        # Player selection with enhanced styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            selected_name = st.selectbox(
                "Select Player for Analysis",
                user_options,
                help="Choose a player to view detailed analytics and performance metrics"
            )
        
        selected_user = next(u for u in users if f"{u.first_name} {u.last_name}" == selected_name)
        player = selected_user.players[0] if selected_user.players else None
        
        st.divider()
        
        # Enhanced player overview with metrics
        with st.container():
            overview_col1, overview_col2, overview_col3 = st.columns([1, 2, 1])
            
            with overview_col1:
                photo_url = getattr(selected_user, "photo_url", None) or "https://images.pexels.com/photos/114296/pexels-photo-114296.jpeg"
                player_number = getattr(player, "number", "N/A") if player else "N/A"
                st.image(photo_url, width=250, caption=f"{selected_name}")
                
                # Quick stats sidebar
                with st.container():
                    st.subheader("Quick Stats")
                    birth_date = pd.to_datetime(selected_user.birth_date, errors="coerce")
                    age = calculate_age(birth_date) if pd.notnull(birth_date) else 0
                    
                    st.metric("Age", f"{age} years")
                    st.metric("Nationality", getattr(player, "nationality", selected_user.country) if player else selected_user.country)
                    primary_pos = getattr(player, "primary_position", "Not specified") if player else "Not specified"
                    st.metric("Primary Position", primary_pos)
            
            with overview_col2:
                st.subheader("Performance Overview")
                
                # Key performance metrics
                perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
                
                registration_date = getattr(player, "registration_date", None) if player else None
                #height = getattr(player, "height", "Not specified") if player else "Not specified"
                grade_level = getattr(player, "grade_level", "Not specified") if player else "Not specified"
                training_location = getattr(player, "training_location", "Not specified") if player else "Not specified"
                
                #with perf_col1:
                    #st.metric("Height", f"{height} cm" if height != "Not specified" else height)
                
                with perf_col2:
                    st.metric("Grade Level", grade_level)
                
                with perf_col3:
                    st.metric("Training Location", training_location)
                
                with perf_col4:
                    dominant_foot = getattr(player, "dominant_foot", "Not specified") if player else "Not specified"
                    st.metric("Dominant Foot", dominant_foot)
                
            
            with overview_col3:
                st.subheader("Player Information")
                
                # Player details from database
                school_name = getattr(player, "school_name", "Not specified") if player else "Not specified"
                education_level = getattr(player, "education_level", "Not specified") if player else "Not specified"
                last_team = getattr(player, "last_team", "Not specified") if player else "Not specified"
                athlete_number = getattr(player, "athlete_number", "Not specified") if player else "Not specified"
                
                details = [
                    ("School", school_name),
                    ("Education Level", education_level),
                    ("Last Team", last_team),
                    ("Athlete Number", str(athlete_number)),
                    ("Registration", str(registration_date) if registration_date else "Not specified")
                ]
                
                for label, value in details:
                    st.text(f"{label}: {value}")
        
        st.divider()
        
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
                        
            with profile_col2:
                st.subheader("Player Details")
                
                # Enhanced player profile using actual database fields
                player_data = [
                    ("Jersey Number", str(getattr(player, "number", "Not assigned")) if player else "Not assigned"),
                    ("Primary Position", getattr(player, "primary_position", "Not specified") if player else "Not specified"),
                    ("Secondary Position", getattr(player, "secondary_position", "Not specified") if player else "Not specified"),
                    ("Dominant Foot", getattr(player, "dominant_foot", "Not specified") if player else "Not specified"),
                    ("Height", f"{getattr(player, 'height', 'Not specified')} cm" if player and getattr(player, 'height') else "Not specified"),
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
                            
                            pdf_bytes = generate_player_report(
                                player_data=player_data,
                                player_teams=pd.DataFrame(),
                                player_games=pd.DataFrame(),
                                player_metrics=pd.DataFrame(),
                                player_evaluations=pd.DataFrame(),
                                player_videos=pd.DataFrame(),
                                player_documents=pd.DataFrame()
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