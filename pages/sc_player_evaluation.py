import streamlit as st
from sqlalchemy import distinct
from sqlalchemy.orm import joinedload
from db import SessionLocal
from models import Players, Users, CoreValue, Programs, PlayerAssessments
from datetime import date, datetime
from utils import util

util.setup_page("Player Evaluation")

st.header(":blue[Players] Evaluation", divider=True)

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
            session.add_all([
                CoreValue(name="Discipline", description="Daily excellence through intentional action. Punctuality, preparation, focus during training, and consistent effort in all activities."),
                CoreValue(name="Wellbeing", description="Holistic care of body and mind. Physical conditioning, injury prevention, nutrition awareness, and overall health management."),
                CoreValue(name="Resilience", description="Strength through adversity. Ability to bounce back from setbacks, handle pressure, and maintain performance under stress."),
                CoreValue(name="Growth Mindset", description="Learning through effort, curiosity, and feedback. Openness to instruction, willingness to try new things, and continuous improvement."),
                CoreValue(name="Teamwork", description="Unity, trust, and shared purpose. Collaboration with teammates, leadership qualities, and positive team dynamics."),
            ])

        if not session.query(Programs).first():
            session.add_all([
                Programs(name="AC RIVER HIGH PERFORMANCE ACADEMY"),
                Programs(name="SA ATHENIANS HIGH PERFORMANCE ACADEMY"),
                Programs(name="AC RIVER YOUTH ACADEMY"),
                Programs(name="SA ATHENIANS YOUTH ACADEMY"),
                Programs(name="MLS GO"),
                Programs(name="SKILLS ACADEMY"),
            ])

        session.commit()

def show_filters():
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

    def save_tab(items, category, comment_key_prefix, slider_max, slider_default, key_prefix):
        ratings = {}
        for idx, item in enumerate(items):
            ratings[item] = st.slider(item, 1, slider_max, slider_default, key=f"{key_prefix}_{idx}")
        comments = st.text_area(f"{category} Comments", key=f"{comment_key_prefix}_comments", height=100)
        if st.button(f"Save {category}", key=f"save_{category}"):
            with SessionLocal() as session:
                for item in items:
                    session.add(PlayerAssessments(
                        player_id=selected.player_id,
                        coach_id=coach_map[evaluator],
                        category=category,
                        core_value_id=None,
                        program_id=prog_inv.get(program),
                        item=item,
                        value=ratings[item],
                        notes=comments,
                        created_at=datetime.now()
                    ))
                session.commit()
            st.success(f"{category} saved ✅")

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

    with tabs[1]:
        st.subheader("Technical Skills (Ball Mastery)")
        save_tab(["First touch", "Dribbling", "Passing accuracy", "Shooting technique", "Overall ball control"], "Técnico", "tech", 5, 3, "tech")

    with tabs[2]:
        st.subheader("Tactical Understanding (Game Model)")
        save_tab(["Understanding of MWB", "Understanding of MNB", "Understanding of transition principles", "Decision-making in different game moments"], "Táctico", "tac", 5, 3, "tac")

    with tabs[3]:
        st.subheader("Physical Performance (High Performance Model)")
        save_tab(["Speed", "Agility", "Strength", "Endurance", "Movement quality"], "Físico", "phys", 5, 3, "phys")

    with tabs[4]:
        st.subheader("Match Performance & Consistency")
        save_tab(["Ability to transfer training to match situations", "Consistency in performance, Impact on team success"], "Colectivo", "match", 5, 3, "match")

    with tabs[5]:
        st.subheader("Leadership & Character Development")
        save_tab(["Embodiment of all five core values", "Positive influence on others", "Character development beyond soccer"], "Mental", "lead", 5, 3, "lead")

def main():
    show_filters()

if __name__ == "__main__":
    main()
