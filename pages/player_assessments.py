import streamlit as st
from functools import partial
from utils import login
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Player, User, Team, PlayerAssessment
from datetime import date
from sqlalchemy.exc import SQLAlchemyError


def calculate_age(birth):
    if not birth:
        return "N/D"
    today = date.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def Setup_page():
    login.generarLogin()
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)


def Assessments_Forms():
    session: Session = SessionLocal()
    st.header("360° PLAYER'S ASSESSMENTS FORMS", divider="gray")

    st.session_state.setdefault("user_id", 1)
    st.session_state.setdefault("role_id", 2)  # ⛔ For demo only
    if st.session_state["role_id"] != 2:
        st.error("COACHES ACCESS ONLY!!!")
        st.stop()

    coach_id = st.session_state["user_id"]
    st.title("📋 Player's Assessments")

    players = (
        session.query(Player)
        .join(User)
        .join(Team)
        .all()
    )

    data = []
    for p in players:
        full_name = f"{p.user.first_name} {p.user.last_name}"
        data.append({
            "player_id": p.player_id,
            "full_name": full_name,
            "birth_date": p.user.birth_date,
            "nationality": p.user.nationality,
            "team_name": p.team.name if p.team else "N/A",
            "photo_url": p.photo_url,
        })

    if not data:
        st.warning("No hay información disponible.")
        st.stop()

    team_options = ["All teams"] + sorted({d["team_name"] for d in data if d["team_name"]})
    team_choice = st.selectbox("Filter by team", team_options, key="sel_team")

    filtered = [d for d in data if team_choice == "All teams" or d["team_name"] == team_choice]

    if not filtered:
        st.info("No players found for this team.")
        st.stop()

    player_names = [d["full_name"] for d in filtered]
    player_choice = st.selectbox("Choose player", ["—"] + player_names, index=0)
    if player_choice == "—":
        st.stop()

    player_data = next(p for p in filtered if p["full_name"] == player_choice)
    player_id = player_data["player_id"]
    photo_url = player_data.get("photo_url") or "https://placehold.co/200x260?text=No+Photo"

    col_img, col_data = st.columns([1, 2])
    with col_img:
        st.image(photo_url, width=180, caption=player_choice)
    with col_data:
        st.markdown(f"**Age:** {calculate_age(player_data['birth_date'])} years")
        st.markdown(f"**Nationality:** {player_data['nationality'] or 'N/D'}")
        st.markdown(f"**Last team:** {player_data['team_name'] or 'N/D'}")

    st.divider()

    if "eval_store" not in st.session_state:
        st.session_state["eval_store"] = {}
    if player_id not in st.session_state["eval_store"]:
        st.session_state["eval_store"][player_id] = {"technical": {}, "physical": {}, "mental": {}}

    player_store = st.session_state["eval_store"][player_id]

    def upsert_store(cat, item, key, notes=False):
        val = st.session_state.get(key, "")
        store = player_store[cat]
        if notes:
            store[f"{item}_notes"] = val
        else:
            store[item] = val

    def save_to_db(cat, item):
        val = player_store[cat].get(item)
        notes = player_store[cat].get(f"{item}_notes", "")
        try:
            assessment = PlayerAssessment(
                player_id=player_id,
                coach_id=coach_id,
                category=cat,
                item=item,
                value=str(val),
                notes=notes,
            )
            session.add(assessment)
            session.commit()
            st.success("✅ Saved to database")
        except SQLAlchemyError as e:
            session.rollback()
            st.error(f"❌ Database error: {e}")

    tab_tech, tab_phys, tab_ment = st.tabs(["Technical", "Physical", "Mental"])

    with tab_tech:
        cat = "technical"
        skill = st.selectbox("Skill", ["Ball Control", "Passing", "Dribbling", "Shooting", "Heading"])
        slider_key = f"{player_id}_{cat}_slider_{skill}"
        notes_key = f"{player_id}_{cat}_notes_{skill}"
        st.slider("Rating (1–5)", 1, 5, player_store[cat].get(skill, 3), key=slider_key, on_change=partial(upsert_store, cat, skill, slider_key, False))
        st.text_area("Coach notes", player_store[cat].get(f"{skill}_notes", ""), key=notes_key, on_change=partial(upsert_store, cat, skill, notes_key, True))
        if st.button("Save", key=f"save_{cat}_{skill}"):
            save_to_db(cat, skill)

    with tab_phys:
        cat = "physical"
        test = st.selectbox("Test", ["30-m Sprint (s)", "Yo-Yo IR1 (level)", "Illinois Agility (s)"])
        input_key = f"{player_id}_{cat}_input_{test}"
        notes_key = f"{player_id}_{cat}_notes_{test}"
        st.text_input("Result (numeric)", player_store[cat].get(test, ""), key=input_key, on_change=partial(upsert_store, cat, test, input_key, False))
        st.text_area("Coach notes", player_store[cat].get(f"{test}_notes", ""), key=notes_key, on_change=partial(upsert_store, cat, test, notes_key, True))
        if st.button("Save", key=f"save_{cat}_{test}"):
            save_to_db(cat, test)

    with tab_ment:
        cat = "mental"
        aspect = st.selectbox("Aspect", ["Motivation", "Focus", "Teamwork", "Discipline"])
        slider_key = f"{player_id}_{cat}_slider_{aspect}"
        notes_key = f"{player_id}_{cat}_notes_{aspect}"
        st.slider("Rating (1–5)", 1, 5, player_store[cat].get(aspect, 3), key=slider_key, on_change=partial(upsert_store, cat, aspect, slider_key, False))
        st.text_area("Coach notes", player_store[cat].get(f"{aspect}_notes", ""), key=notes_key, on_change=partial(upsert_store, cat, aspect, notes_key, True))
        if st.button("Save", key=f"save_{cat}_{aspect}"):
            save_to_db(cat, aspect)


def main():
    Setup_page()
    Assessments_Forms()

if __name__ == "__main__":
    main()

