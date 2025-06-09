import streamlit as st
from functools import partial
from utils import login
import pandas as pd
import numpy as np
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime
from sc_app.queries import SQL_PLAYERS2
import random

#Versión DEMO para intriducir forms de evaluación de jugadores.


# Función para inicializar la conexión a la base de datos y cachearla
@st.cache_resource
def connect_to_db():
    try:
        # Intentamos obtener la conexión definida en los secrets
        conn = st.connection('mysql', type='sql')
        #st.success("Conexión establecida correctamente")
    except Exception as e:
        # Si ocurre algún error, lo capturamos y mostramos un mensaje en la aplicación
        st.error("Error al conectar con la base de datos:")
        st.error(e) 
    return conn

# Función para calcular la edad

def calculate_age(birth):
    if pd.isna(birth):
        return "N/D"
    today = pd.Timestamp.today().date()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def Setup_page():
    login.generarLogin()
    #st.set_page_config(layout="wide", initial_sidebar_state="auto", menu_items=None)
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)


def Assessments_Forms():
    #Creación FORMS de evaluación de jugadores.
    
    # Conexión a DB*******************
    dbconn = connect_to_db()
       
    #Preparación de la página**********************************************************************
    st.header("360° PLAYER'S ASSESSMENTS FORMS", divider="gray")
    
    # El Usuario podrá escoger el jugador a su cargo.
    st.session_state.setdefault("user_id", 1)
    st.session_state.setdefault("role_id",   2)   #Forzando Ingreso para Demo
    if st.session_state["role_id"] != 2:          # ⛔ solo coaches
        st.error("COACHES ACCESS ONLY!!!")
        st.stop()

    coach_id = st.session_state["user_id"]
    st.title("📋 Player's Assessments")
    user_id = st.session_state["user_id"]
    df = dbconn.query(SQL_PLAYERS2, ttl=600)
    
    if df.empty:
        st.warning("No hay información disponible.")
        st.stop()

    # ──────────────────────── LISTA DE EQUIPOS ──────────────────────────────
    team_options = (
        ["All teams"] +
        sorted(df["team_name"].dropna().unique().tolist())
    )
    team_choice = st.selectbox("Filter by team", team_options, key="sel_team",)

    # DataFrame filtrado
    df_view = (
        df if team_choice == "All teams"
        else df.query("team_name == @team_choice")
    )

    if df_view.empty:
        st.info("No players found for this team.")
        st.stop()

    # ────────────────────────── SELECTBOX DE JUGADOR ───────────────────────
    player_options = df_view["full_name"].tolist()
    player_choice = st.selectbox(
        "Choose player", 
        ["—"] + player_options,           # placeholder
        index=0,
        key="sel_player",
    )

    if player_choice == "—":             # aún no eligió
        st.stop()

    player_row = df_view.loc[df_view.full_name == player_choice].squeeze()
    player_id  = int(player_row["player_id"])
    st.success(f"Chosen Player: {player_choice}")
    # ────────────────────────────  Visualizando "PLAYER CARD" para guiar al evaluador  ───────────────────────────────
    placeholder = "https://placehold.co/200x260?text=No+Photo"

    photo = (
        player_row["photo_url"]
        if pd.notna(player_row["photo_url"]) and str(player_row["photo_url"]).strip()
        else placeholder
    )

    col_img, col_data = st.columns([1, 2])
    with col_img:
        st.image(photo, width=180, caption=player_choice)
    with col_data:
        st.markdown(f"**Age:** {calculate_age(player_row["birth_date"])} years")
        st.markdown(f"**Nationality:** {player_row["nationality"] or 'N/D'}")
        st.markdown(f"**Last team:** {player_row['team_name'] or 'N/D'}")

    st.divider()
   
    # ────────────────────────────  STATE-HELPERS  ───────────────────────────────
    def upsert_store(player_id: int, cat: str, item: str, key: str, notes=False):
        """Generic updater called by every on_change."""
        val   = st.session_state.get(key, "")
        store = st.session_state["eval_store"][player_id][cat]
        if notes:
            store[f"{item}_notes"] = val
        else:
            store[item] = val

    def save_to_db(cat, item):
        """Commit latest value for *this* player/item to DB."""
        val   = player_store[cat].get(item)
        notes = player_store[cat].get(f"{item}_notes", "")
        #_insert_eval(player_id, coach_id, cat, item, str(val), notes)
        st.markdown("#### UNDER CONSTRUCTION")
        st.success("✅ Saved to database")
    
    
    
    #  Tabs por categoría de evaluación ───────────────────────────────────────
    tab_tech, tab_phys, tab_ment = st.tabs(["Technical", "Physical", "Mental"])
    # ─────────────────── CONFIGURACIÓN DE ESTADO PERSISTENTE ────────────────────
    # ───────── Session bootstrap AFTER the player is chosen ─────────
    # Key structure →  eval_store[PLAYER_ID][CATEGORY][ITEM] = value
    if "eval_store" not in st.session_state:
        st.session_state["eval_store"] = {}

    if player_id not in st.session_state["eval_store"]:
        st.session_state["eval_store"][player_id] = {"technical": {}, "physical":  {}, "mental":    {}, }
    
    player_store = st.session_state["eval_store"].setdefault(
        player_id,
        {"technical": {}, "physical": {}, "mental": {}},
    )
    # ─────────────── TAB 1 · TECHNICAL ────────────────────────────────────────────
    with tab_tech:
        cat   = "technical"
        skill = st.selectbox(
            "Skill",
            ["Ball Control", "Passing", "Dribbling", "Shooting", "Heading"],
            key=f"{player_id}_{cat}_select",
        )
        # ------- create unique keys per player + item -------
        slider_key = f"{player_id}_{cat}_slider_{skill.replace(' ', '_')}"
        notes_key  = f"{player_id}_{cat}_notes_{skill.replace(' ', '_')}"
        # ------- pick default values from player_store -------
        start_rating = player_store[cat].get(skill, 3)
        start_notes  = player_store[cat].get(f"{skill}_notes", "")
        # ------- widgets with on_change callbacks ------------
        st.slider(
            "Rating (1–5)",
            min_value=1,
            max_value=5,
            value=start_rating,
            key=slider_key,
            on_change=partial(upsert_store,
                            player_id, cat, skill, slider_key, notes=False),
        )
        st.text_area(
            "Coach notes",
            value=start_notes,
            key=notes_key,
            height=100,
            on_change=partial(upsert_store,
                            player_id, cat, skill, notes_key, notes=True),
        )
        # Save button
        if st.button("Save", key=f"{player_id}_{cat}_save_{skill}"):
            save_to_db(cat, skill)

    # ─────────────── TAB 2 PHYSICAL ────────────────────────────────────────────────────────────────
    with tab_phys:
        cat  = "physical"
        test = st.selectbox(
            "Physical test",
            ["30-m Sprint (s)", "Yo-Yo IR1 (level)", "Illinois Agility (s)"],
            key=f"{player_id}_{cat}_select",
        )

        input_key = f"{player_id}_{cat}_input_{test.replace(' ', '_')}"
        notes_key = f"{player_id}_{cat}_notes_{test.replace(' ', '_')}"

        st.text_input(
            "Result (numeric)",
            value=player_store[cat].get(test, ""),
            key=input_key,
            on_change=partial(upsert_store, player_id, cat, test, input_key, False),
        )
        st.text_area(
            "Coach notes",
            value=player_store[cat].get(f"{test}_notes", ""),
            key=notes_key,
            on_change=partial(upsert_store, player_id, cat, test, notes_key, True),
            height=100,
        )
        if st.button("Save", key=f"btn_save_{player_id}_{cat}_{test}"):
            save_to_db(cat, test)       

     # ─────────────── TAB 3 MENTAL ────────────────────────────────────────────────────────────────
    with tab_ment:
        cat = "mental"

        aspect = st.selectbox(
            "Aspect",
            ["Motivation", "Focus", "Teamwork", "Discipline"],
            key=f"{player_id}_{cat}_select",
        )

        slider_key = f"{player_id}_{cat}_slider_{aspect}"
        notes_key  = f"{player_id}_{cat}_notes_{aspect}"

        # Rating (slider)
        st.slider(
            "Rating (1–5)",
            1, 5,
            value=player_store[cat].get(aspect, 3),
            key=slider_key,
            on_change=partial(upsert_store, player_id, cat, aspect, slider_key, False),
        )

        # Coach notes
        st.text_area(
            "Coach notes",
            value=player_store[cat].get(f"{aspect}_notes", ""),
            key=notes_key,
            on_change=partial(upsert_store, player_id, cat, aspect, notes_key, True),
            height=100,
        )

        if st.button("Save", key=f"{player_id}_{cat}_save_{aspect}"):
            save_to_db(cat, aspect)
   


def main():

    Setup_page()
    Assessments_Forms() 

if __name__ == "__main__":
    main() 