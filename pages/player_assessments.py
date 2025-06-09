import streamlit as st
from sqlalchemy.orm import Session
from db import SessionLocal
from utils import login
from models import PlayerAssessments, Players, Users
import datetime

def Setup_page():
    login.generarLogin()
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)

def show_player_assessments_page():
    st.title("Evaluaciones de Jugadores")

    session: Session = SessionLocal()

    # Listado de jugadores disponibles
    jugadores = session.query(Players).all()
    jugadores_dict = {f"{p.player_id} - {p.user.first_name} {p.user.last_name}": p.player_id for p in jugadores if p.user}
    jugador_seleccionado = st.selectbox("Selecciona un jugador:", list(jugadores_dict.keys()))

    player_id = jugadores_dict[jugador_seleccionado]

    # Evaluaciones del jugador seleccionado
    evaluaciones = session.query(PlayerAssessments).filter_by(player_id=player_id).all()

    st.subheader("Evaluaciones existentes")
    for idx, eval in enumerate(evaluaciones):
        with st.expander(f"{eval.category}: {eval.item} ({eval.value}) - {eval.created_at.date()}"):
            st.write(f"Notas: {eval.notes or 'Sin notas'}")
            st.write(f"Coach: {eval.coach.first_name if eval.coach else 'Desconocido'}")

    st.divider()

    st.subheader("Agregar nueva evaluación")
    coach_id = session.query(Users).filter(Users.role.has(role_name="Coach")).first().user_id  # ⚠️ reemplazar con actual usuario coach si se tiene
    category = st.selectbox("Categoría", ["technical", "physical", "mental"])
    item = st.text_input("Ítem evaluado")
    value = st.text_input("Valor")
    notes = st.text_area("Notas", placeholder="Notas adicionales del coach (opcional)")
    btn = st.button("Guardar evaluación")

    if btn:
        nueva_eval = PlayerAssessments(
            player_id=player_id,
            coach_id=coach_id,
            category=category,
            item=item,
            value=value,
            notes=notes,
            created_at=datetime.datetime.utcnow()
        )
        session.add(nueva_eval)
        session.commit()
        st.success("✅ Evaluación guardada correctamente")
        st.rerun()

def main():
    Setup_page()
    show_player_assessments_page()

if __name__ == "__main__":
    main()