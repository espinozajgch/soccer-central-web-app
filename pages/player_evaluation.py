import streamlit as st
from sqlalchemy.orm import Session, joinedload
from db.db import SessionLocal
from utils import login
from db.models import PlayerAssessments, Players, Users
from db.db import get_db_session
import datetime
from utils import util

util.setup_page("Player Evaluation")

# LOGIN + MENU
util.login_if_needed()

st.header(":blue[Players] Evaluation", divider=True)

def show_player_assessments_page():

  with get_db_session() as session:

    # Cargamos todos los jugadores con su usuario relacionado
    jugadores = session.query(Players).options(joinedload(Players.user)).join(Users).filter(Players.user_id == Users.user_id).all()

    # Extraemos valores únicos para los filtros
    posiciones = sorted({p.primary_position for p in jugadores if p.primary_position})
    escuelas = sorted({p.school_name for p in jugadores if p.school_name})
    numeros = sorted({p.number for p in jugadores if p.number is not None})
    anios_nacimiento = sorted({u.birth_date.year for p in jugadores if p.user and p.user.birth_date for u in [p.user]})
    equipos = sorted({p.last_team for p in jugadores if p.last_team})

    # Formulario con selectores dinámicos
    with st.form("form_filtros"):
        col1, col2 = st.columns(2)
        with col1:
            filtro_nombre = st.text_input("Nombre o Apellido contiene")
            filtro_posicion = st.selectbox("Posición primaria", [""] + posiciones)
            filtro_escuela = st.selectbox("Escuela", [""] + escuelas)
        with col2:
            filtro_numero = st.selectbox("Número de camiseta", [""] + [str(n) for n in numeros])
            filtro_anio = st.selectbox("Año de nacimiento", [""] + [str(a) for a in anios_nacimiento])
            filtro_equipo = st.selectbox("Último equipo", [""] + equipos)

        aplicar_filtro = st.form_submit_button("Aplicar filtros")

    # Construimos la query dinámica
    query = session.query(Players).options(joinedload(Players.user)).join(Users).filter(Players.user_id == Users.user_id)


    if filtro_nombre:
        query = query.filter(
            (Users.first_name.ilike(f"%{filtro_nombre}%")) |
            (Users.last_name.ilike(f"%{filtro_nombre}%"))
        )
    if filtro_posicion:
        query = query.filter(Players.primary_position == filtro_posicion)
    if filtro_escuela:
        query = query.filter(Players.school_name == filtro_escuela)
    if filtro_numero:
        query = query.filter(Players.number == int(filtro_numero))
    if filtro_anio:
        query = query.filter(Users.birth_date.like(f"{filtro_anio}-%"))
    if filtro_equipo:
        query = query.filter(Players.last_team == filtro_equipo)

    # Ejecutamos
    jugadores_filtrados = query.all()

    # Mostramos el selectbox si hay resultados
    if not jugadores_filtrados:
        st.warning("No se encontraron jugadores con esos filtros.")
    else:
        jugadores_dict = {
            f"{p.player_id} | {p.user.first_name} {p.user.last_name} | #{p.number or ''} | {p.primary_position or ''}": p.player_id
            for p in jugadores_filtrados
        }
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
        coach_id = session.query(Users).filter(Users.email == st.session_state.usuario).first().user_id
        category = st.selectbox("Categoría", ["technical", "physical", "mental"])
        item = st.text_input("Ítem evaluado")
        value = st.slider("Valor", min_value=1, max_value=5, step=1)
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
    show_player_assessments_page()

if __name__ == "__main__":
    main()