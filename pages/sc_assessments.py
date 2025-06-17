import streamlit as st
from sqlalchemy import distinct, extract, Index, ForeignKeyConstraint, Enum as SqlEnum
from sqlalchemy.orm import joinedload
from db import SessionLocal
from utils import login
from models import Players, Users, CoreValue, Programs, PlayerAssessments
from datetime import date, datetime
from typing import List, Optional

# Estilos y colores
BRAND_COLORS = ['#d4bc64', '#84ccb4', '#5c74b4', '#6c6c84', '#504f8f', '#83c3d4', '#646c84', '#646c7c', '#588898', '#586c9c']

def color_html(text: str, color: str, bold: bool = True):
    weight = 'bold' if bold else 'normal'
    return f"<span style='color:{color}; font-weight:{weight}'>{text}</span>"

def calc_age(birthdate: date) -> int:
    today = date.today()
    return (today.year - birthdate.year) - ((today.month, today.day) < (birthdate.month, birthdate.day))

@st.cache_resource
def init_core_values_and_programs():
    with SessionLocal() as session:
        if not session.query(CoreValue).first():
            core_values = [
                CoreValue(name="Discipline", description="Daily excellence through intentional action. Punctuality, preparation, focus during training, and consistent effort in all activities."),
                CoreValue(name="Wellbeing", description="Holistic care of body and mind. Physical conditioning, injury prevention, nutrition awareness, and overall health management."),
                CoreValue(name="Resilience", description="Strength through adversity. Ability to bounce back from setbacks, handle pressure, and maintain performance under stress."),
                CoreValue(name="Growth Mindset", description="Learning through effort, curiosity, and feedback. Openness to instruction, willingness to try new things, and continuous improvement."),
                CoreValue(name="Teamwork", description="Unity, trust, and shared purpose. Collaboration with teammates, leadership qualities, and positive team dynamics."),
            ]
            session.add_all(core_values)

        if not session.query(Programs).first():
            programs = [
                Programs(name="AC RIVER HIGH PERFORMANCE ACADEMY"),
                Programs(name="SA ATHENIANS HIGH PERFORMANCE ACADEMY"),
                Programs(name="AC RIVER YOUTH ACADEMY"),
                Programs(name="SA ATHENIANS YOUTH ACADEMY"),
                Programs(name="MLS GO"),
                Programs(name="SKILLS ACADEMY"),
            ]
            session.add_all(programs)

        session.commit()

def show_filters():
    login.generarLogin()
    st.title("**Soccer Central Player Performance Evaluation**")
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)

    # Inicializar datos Core Values y Programs
    init_core_values_and_programs()

    with SessionLocal() as session:
        players = session.query(Players).join(Players.user).options(joinedload(Players.user)).filter(Users.role_id == 4).all()
        posiciones = [row[0] for row in session.query(distinct(Players.primary_position)).filter(Players.primary_position.isnot(None)).all() if row[0]]
        coaches = session.query(Users).filter(Users.role_id == 2).all()
        core_vals = session.query(CoreValue).all()
        programs = session.query(Programs).all()

    if not players:
        st.warning("No se encontraron jugadores en la base de datos.")
        return

    def fmt_player(i):
        p = players[i]
        bd = p.user.birth_date
        age = calc_age(bd) if bd else "N/A"
        return f"{p.user.first_name} {p.user.last_name} ({age} years)"

    idx = st.selectbox("Player Name", range(len(players)), format_func=fmt_player)
    selected = players[idx]
    age = calc_age(selected.user.birth_date)

    default_group = "U6-U8" if age <= 8 else "U9-U10" if age <= 10 else "U11-U12" if age <= 12 else "U13-U15" if age <= 15 else "U16-U19"
    age_groups = ["U6-U8", "U9-U10", "U11-U12", "U13-U15", "U16-U19"]

    coach_map = {f"{c.first_name} {c.last_name}": c.user_id for c in coaches}
    program_map = {p.id: p.name for p in programs}
    prog_inv = {v: k for k, v in program_map.items()}
    program_opts = [""] + list(program_map.values())
    position_opts = [""] + sorted(posiciones)

    st.subheader("Setting Filters", divider="blue")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.text_input("Player Name", value=f"{selected.user.first_name} {selected.user.last_name} ({age} years)", disabled=True)
        age_group = st.selectbox("Age Group", age_groups, index=age_groups.index(default_group))
    with col2:
        position = st.selectbox("Position", position_opts, index=position_opts.index(selected.primary_position) if selected.primary_position in position_opts else 0)
        evaluation_date = st.date_input("Evaluation Date", value=date.today())
    with col3:
        evaluator = st.selectbox("Coach/Evaluator", list(coach_map.keys()))
        program = st.selectbox("Program", program_opts)

    st.markdown("---")
    st.write("**Filtros seleccionados:**")
    st.write(f"- Player Name: {selected.user.first_name} {selected.user.last_name}")
    st.write(f"- Age Group: {age_group}")
    st.write(f"- Position: {position}")
    st.write(f"- Evaluation Date: {evaluation_date}")
    st.write(f"- Coach/Evaluator: {evaluator}")
    st.write(f"- Program: {program}")

    tab_labels = [
        "1. Core Values",
        "2. Technical Skills (Ball Mastery)",
        "3. Tactical Understanding (Game Model)",
        "4. Physical Performance (High Performance Model)",
        "5. Match Performance & Consistency",
        "6. Leadership & Character Development"
    ]
    tabs = st.tabs(tab_labels)

    def save_assessments(items, scores, comments, category):
        with SessionLocal() as session:
            for item, score in scores.items():
                session.add(PlayerAssessments(
                    player_id=selected.player_id,
                    coach_id=coach_map[evaluator],
                    category=category,
                    core_value_id=None,
                    program_id=prog_inv.get(program),
                    item=item,
                    value=score,
                    notes=comments
                ))
            session.commit()

    # Tab 1: Core Values
    with tabs[0]:
        st.subheader("Core Values")
        ratings_cv = {}
        comments_cv = {}
        for idx, val in enumerate(core_vals):
            c = BRAND_COLORS[idx % len(BRAND_COLORS)]
            st.markdown(color_html(val.name.upper(), c), unsafe_allow_html=True)
            ratings_cv[val.name] = st.slider(val.name, 1, 10, 5, key=f"cv_{idx}")
            st.caption(val.description or "")
            comments_cv[val.name] = st.text_area(f"Comments for {val.name}", placeholder="Your observations here...!", key=f"comment_{idx}", height=80)
            st.write("---")

        if st.button("Save Core Values", key="save_core"):
            with SessionLocal() as session:
                for val in core_vals:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category="Valores",
                        core_value_id=val.id,
                        program_id=prog_inv.get(program),
                        item=val.name,
                        value=ratings_cv[val.name],
                        notes=comments_cv[val.name],
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success("¡Core Values saved!")

    # Tab 2: Technical Skills
    with tabs[1]:
        st.subheader("Technical Skills (Ball Mastery)")
        tech_items = ["First touch", "Dribbling", "Passing accuracy", "Shooting technique", "Overall ball control"]
        ratings_tech = {}
        for idx, item in enumerate(tech_items):
            ratings_tech[item] = st.slider(item, 1, 5, 3, key=f"tech_{item}")
        comments_tech = st.text_area("Technical skills comments", key="comments_tech", height=100)

        if st.button("Save Technical", key="save_tech"):
            with SessionLocal() as session:
                for item in tech_items:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category="Técnico",
                        core_value_id=None,
                        program_id=prog_inv.get(program),
                        item=item,
                        value=ratings_tech[item],
                        notes=comments_tech,
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success("Technical Skills saved ✅")

    # Tab 3: Tactical Understanding
    with tabs[2]:
        st.subheader("Tactical Understanding (Game Model)")
        tactical_items = ["Understanding of MWB", "Understanding of MNB", "Understanding of transition principles", "Decision-making in different game moments"]
        ratings_tac = {}
        for idx, item in enumerate(tactical_items):
            ratings_tac[item] = st.slider(item, 1, 5, 3, key=f"tac_{item}")
        comments_tac = st.text_area("Tactical Comments", key="comments_tac", height=100)

        if st.button("Save Tactical", key="save_tac"):
            with SessionLocal() as session:
                for item in tactical_items:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category="Táctico",
                        core_value_id=None,
                        program_id=prog_inv.get(program),
                        item=item,
                        value=ratings_tac[item],
                        notes=comments_tac,
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success("Tactical Understanding guardada ✅")

    # Tab 4: Physical Performance
    with tabs[3]:
        st.subheader("Physical Performance (High Performance Model)")
        phys_items = ["Speed", "Agility", "Strength", "Endurance", "Movement quality"]
        ratings_phys = {}
        for idx, item in enumerate(phys_items):
            ratings_phys[item] = st.slider(item, 1, 5, 3, key=f"phys_{item}")
        comments_phys = st.text_area("Physical Performance Comments", key="comments_phys", height=100)

        if st.button("Save Physical", key="save_phys"):
            with SessionLocal() as session:
                for item in phys_items:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category="Físico",
                        core_value_id=None,
                        program_id=prog_inv.get(program),
                        item=item,
                        value=ratings_phys[item],
                        notes=comments_phys,
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success("Physical Performance guardada ✅")

    # Tab 5: Match Performance & Consistency
    with tabs[4]:
        st.subheader("Match Performance & Consistency")
        match_items = ["Ability to transfer training to match situations", "Consistency in performance, Impact on team success"]
        ratings_match = {}
        for idx, item in enumerate(match_items):
            ratings_match[item] = st.slider(item, 1, 5, 3, key=f"match_{item}")
        comments_match = st.text_area("Match Performance Comments", key="comments_match", height=100)

        if st.button("Save Match Perf & Cons.", key="save_match"):
            with SessionLocal() as session:
                for item in match_items:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category="Colectivo",
                        core_value_id=None,
                        program_id=prog_inv.get(program),
                        item=item,
                        value=ratings_match[item],
                        notes=comments_match,
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success("Match Performance guardada ✅")

    # Tab 6: Leadership & Character Development
    with tabs[5]:
        st.subheader("Leadership & Character Development")
        lead_items = ["Embodiment of all five core values", "Positive influence on others", "Character development beyond soccer"]
        ratings_lead = {}
        for idx, item in enumerate(lead_items):
            ratings_lead[item] = st.slider(item, 1, 5, 3, key=f"lead_{item}")
        comments_lead = st.text_area("Leadership Comments", placeholder="Your comments here…!", key="comments_lead", height=100)

        if st.button("Save Leadership & Character", key="save_lead"):
            with SessionLocal() as session:
                for item in lead_items:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category="Mental",
                        core_value_id=None,
                        program_id=prog_inv.get(program),
                        item=item,
                        value=ratings_lead[item],
                        notes=comments_lead,
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success("Leadership & Character guardada ✅")

def main():
    show_filters()

if __name__ == "__main__":
    main()

