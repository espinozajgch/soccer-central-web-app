import streamlit as st
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from db.db import SessionLocal
from db.models import Players, Users, CoreValue, Programs, PlayerAssessments
from datetime import datetime, date
from utils import util

util.setup_page("Player Evaluation")

# LOGIN + MENU
util.login_if_needed()

st.header("Players Evaluation", divider=True)

# Rayner colours
BRAND_COLORS =util.get_brand_colors_list()
primary, secondary, tertiary = BRAND_COLORS[0], BRAND_COLORS[1], BRAND_COLORS[2]
# ---------------------------------------------------------------------------------
# Inicializadción de flags en session_state para controlar progreso de evaluación.
if "completed_tabs" not in st.session_state:
    st.session_state.completed_tabs = set()

if "edit_batch" not in st.session_state:
    st.session_state.edit_batch = {}


ALL_TABS = {"core", "tech", "tac", "phys", "match", "lead"}
TAB_LABELS = [
    ("core",  "1. Core Values"),
    ("tech",  "2. Technical Skills"),
    ("tac",   "3. Tactical Understanding"),
    ("phys",  "4. Physical Performance"),
    ("match", "5. Match Performance"),
    ("lead",  "6. Leadership & Character")
]

RAW_SPECS = {
    "tech": [
        "First touch", "Dribbling", "Passing accuracy",
        "Shooting technique", "Overall ball control"
    ],
    "tac": [
        "Understanding of MWB", "Understanding of MNB",
        "Transition principles", "Decision-making in different game moments"
    ],
    "phys": [
        "Speed", "Agility", "Strength",
        "Endurance", "Movement quality"
    ],
    "match": [
        "Ability to transfer training to match situations",
        "Consistency in performance, Impact on team success"
    ],
    "lead": [
        "Embodiment of all five core values",
        "Positive influence on others",
        "Character development beyond soccer"
    ],
}

TOTAL_CATS = len(ALL_TABS)

def color_html(text: str, color: str, bold: bool = True):
    weight = 'bold' if bold else 'normal'
    return f"<span style='color:{color}; font-weight:{weight}'>{text}</span>"

def calc_age(birthdate: date) -> int:
    today = date.today()
    return (today.year - birthdate.year) - ((today.month, today.day) < (birthdate.month, birthdate.day))

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

# --------------------------------------------------
def process_assessment_tab(
    tab,
    player_id, coach_id, program_id,
    items,
    category,  
    tab_key,
    slider_max,
    slider_default,
    evaluation_date
):
    """Genera UI de revisión, edición, borrado y guardado para una categoría."""
    with tab:
        st.subheader(category)
        subcats = [it.get("category", category) for it in items]

        prev_map = {}

        # Precarga valores previos para jugador/coach/fecha
        with SessionLocal() as session:
            prev_rows = (
                session.query(PlayerAssessments).filter(
                                                    PlayerAssessments.player_id ==player_id, 
                                                    PlayerAssessments.coach_id == coach_id,
                                                    PlayerAssessments.program_id == program_id,
                                                    func.date(PlayerAssessments.created_at) == evaluation_date,
                                                    PlayerAssessments.category.in_(subcats)
                                                )
                                                .order_by(PlayerAssessments.created_at.desc())
                                                .all() 
            )
        last_ts = None
        if prev_rows:
            last_ts   = prev_rows[0].created_at
            last_rows = [r for r in prev_rows if r.created_at == last_ts]

            with st.expander("Last Evaluation", expanded=True):
                st.write(f"Date: {last_ts.strftime('%Y-%m-%d %H:%M')}")
                for r in last_rows:
                    st.write(f"- {r.item}: {r.value}")
                    # Edit / Delete botones sólo para el último
                col_edit, col_del = st.columns(2)
                suffix = int(last_ts.timestamp())
                    # Capture clicks
                if col_edit.button("\u270F\uFE0F Edit Last",   key=f"edit_{tab_key}_{suffix}"):
                    st.session_state[f"confirm_edit_{tab_key}"] = last_ts 
                if col_del.button("\U0001F5D1\U0000FE0F Delete Last", 
                                  key=f"delete_{tab_key}_{suffix}"):
                    st.session_state[f"confirm_delete_{tab_key}"] = last_ts
        else:
            st.write("No previous evaluation found.")
        # Edit
        edit_flag = f"confirm_edit_{tab_key}"
        if st.session_state.get(edit_flag):
            ts = st.session_state.get(edit_flag, last_ts)
            st.info("Are you sure you want to edit the last evaluation?")
            col_yes, col_cancel = st.columns(2)
            confirm = col_yes.button("Yes, Edit", key=f"yes_edit_{tab_key}")
            cancel  = col_cancel.button("Cancel",     key=f"no_edit_{tab_key}")
            if confirm:
                # marcamos para borrado real en el botón global
                st.session_state.edit_batch[tab_key] = ts
                # cerramos el diálogo
                del st.session_state[edit_flag]
            if cancel:
                # solo cerramos sin marcar nada
                del st.session_state[edit_flag]
        # Confirm Delete
        del_flag = f"confirm_delete_{tab_key}"
        if st.session_state.get(del_flag):
            ts = st.session_state.get(del_flag, last_ts)
            st.warning("This action cannot be undone. Delete all this evaluation?")
            col_yes, col_cancel = st.columns(2)
            confirm = col_yes.button("Yes, delete", key=f"yes_delete_{tab_key}")
            cancel  = col_cancel.button("Cancel",     key=f"no_delete_{tab_key}")

            if confirm:
                # marcamos para borrado real en el botón global
                st.session_state.delete_batch[tab_key] = ts
                del st.session_state[del_flag]
                st.rerun()

            if cancel:
                # solo cerramos sin marcar nada
                del st.session_state[del_flag]
                st.rerun()
        edit_ts = st.session_state.edit_batch.get(tab_key)
        if edit_ts:
            with SessionLocal() as session:
                edit_rows = (
                    session.query(PlayerAssessments)
                           .filter(
                               PlayerAssessments.player_id    == player_id,
                               PlayerAssessments.coach_id     == coach_id,
                               PlayerAssessments.program_id   == program_id,
                               func.date(PlayerAssessments.created_at) == evaluation_date,
                               PlayerAssessments.category     == category,
                               PlayerAssessments.created_at   == edit_ts
                           )
                           .all()
                )
        else:
            edit_rows = []

        #Render sliders
        prev_map = {r.item: r for r in edit_rows}
        for idx, it in enumerate(items):
            slider_key = f"{tab_key}_slider_{idx}"
            default = prev_map[it["item"]].value if it["item"] in prev_map \
                      else st.session_state.get(slider_key, slider_default)
            st.slider(
                it["item"],
                min_value=1,
                max_value=slider_max,
                value=default,
                key=slider_key,
                help="Scale 1–10: 1=low, 10=high"
            )
        #Render comments textarea
        notes_key = f"notes_{tab_key}"
        if notes_key not in st.session_state:
            st.session_state[notes_key] = edit_rows[0].notes if edit_rows else ""
        st.text_area(
            "Comments",
            value=st.session_state[notes_key],
            key=notes_key,
            height=100
        )
# --------------------------------------------------------------------------------------------------
def show_filters():
    init_core_values_and_programs()
    if "show_prev_expander" not in st.session_state:
        st.session_state.show_prev_expander = False
    if "delete_batch" not in st.session_state:
        st.session_state.delete_batch = {}

    with SessionLocal() as session:
        players   = (
            session.query(Players)
                   .join(Players.user)
                   .options(joinedload(Players.user))
                   .filter(Users.role_id == 4)
                   .all()
        )
        core_vals = session.query(CoreValue).all()
        coaches   = session.query(Users).filter(Users.role_id == 2).all()
        programs  = session.query(Programs).all()
    if not players:
        st.warning("No players found in the database.")
        return
    def fmt_player(i):
        p   = players[i]
        bd  = p.user.birth_date
        age = calc_age(bd) if bd else "N/A"
        return f"{p.user.first_name} {p.user.last_name} ({age} years)"
    player_labels = [fmt_player(i) for i in range(len(players))]
    coach_labels  = [f"{c.first_name} {c.last_name}" for c in coaches]
    program_labels = [""] + [p.name for p in programs]
    coach_map   = {name:  c.user_id for name,  c in zip(coach_labels, coaches)}
    program_map = {p.name: p.id      for p in programs}
    #Cambio a único form para todos los filtros.
    with st.form("filters_form"):
        selected_player_idx = st.selectbox(
            "Player",
            options=range(len(players)),
            format_func=lambda i: player_labels[i]
        )
        selected_coach_name   = st.selectbox("Coach",   coach_labels)
        selected_program_name = st.selectbox("Program", program_labels)
        selected_date         = st.date_input(
                                   "Evaluation Date",
                                   value=date.today()
                               )
        apply_filters = st.form_submit_button("Apply Filters")

    if apply_filters:
        st.session_state.selected_player_index = selected_player_idx
        st.session_state.selected_player_id    = players[selected_player_idx].player_id
        st.session_state.selected_coach_name   = selected_coach_name
        st.session_state.selected_coach_id     = coach_map[selected_coach_name]
        st.session_state.selected_program_name = selected_program_name
        st.session_state.selected_program_id   = program_map.get(selected_program_name)
        st.session_state.evaluation_date       = selected_date

        last_pid = st.session_state.get("last_player_id")
        new_pid  = st.session_state.selected_player_id
        if last_pid != new_pid:
            st.session_state.completed_tabs     = set()
            st.session_state.edit_batch         = {}
            st.session_state.show_prev_expander = False
            st.session_state.last_player_id     = new_pid

    # Defaults para la primera carga (si no existe aún selected_* en session_state)
    if "selected_player_id" not in st.session_state:
        st.session_state.selected_player_index = 0
        st.session_state.selected_player_id    = players[0].player_id
        st.session_state.selected_coach_name   = coach_labels[0]
        st.session_state.selected_coach_id     = coach_map[coach_labels[0]]
        st.session_state.selected_program_name = program_labels[0]
        st.session_state.selected_program_id   = program_map.get(program_labels[0])
        st.session_state.evaluation_date       = date.today()
        st.session_state.last_player_id        = st.session_state.selected_player_id

    st.subheader("Current Filters", divider="blue")
    st.markdown(f"**Player:** {player_labels[st.session_state.selected_player_index]}")
    st.markdown(f"**Coach:** {st.session_state.selected_coach_name}")
    st.markdown(f"**Program:** {st.session_state.selected_program_name or 'N/A'}")
    st.markdown(f"**Date:** {st.session_state.evaluation_date}")

    pid        = st.session_state.selected_player_id
    cid        = st.session_state.selected_coach_id
    prog       = st.session_state.selected_program_id
    eval_date  = st.session_state.evaluation_date

    with SessionLocal() as session:
        has_any = session.query(PlayerAssessments)\
                         .filter(
                             PlayerAssessments.player_id    == pid,
                             PlayerAssessments.coach_id     == cid,
                             PlayerAssessments.program_id   == prog,
                             func.date(PlayerAssessments.created_at) == eval_date
                         ).first() is not None

    if has_any:
        st.session_state.show_prev_expander = True
        # load saved categories
        with SessionLocal() as session:
            saved = session.query(PlayerAssessments.category)\
                           .filter(
                               PlayerAssessments.player_id    == pid,
                               PlayerAssessments.coach_id     == cid,
                               PlayerAssessments.program_id   == prog,
                               func.date(PlayerAssessments.created_at) == eval_date
                           ).distinct().all()
        saved_cats = {c for (c,) in saved}
        st.session_state.completed_tabs = { key for key,label in TAB_LABELS if label in saved_cats }

    # Show previous batches
    if st.session_state.show_prev_expander:
        with st.expander("Previous Evaluations"):
            with SessionLocal() as session:
                last_dates = session.query(PlayerAssessments.created_at)\
                                    .filter_by(player_id=pid, coach_id=cid, program_id=prog)\
                                    .distinct()\
                                    .order_by(PlayerAssessments.created_at.desc())\
                                    .limit(5).all()
            for (ts,) in last_dates: 
                st.write(
                    ts.strftime("%Y-%m-%d %H:%M")
                )

    items_core = [{"item": cv.name, "core_value_id": cv.id, 
                   "category": f"Core Value {i+1}"}for i, cv in enumerate(core_vals)]
    #Control de Progreso de Evaluación y visualización.
    labels_with_marks = [
        f"{'\u2705\uFE0F' if key in st.session_state.completed_tabs else ''} {label}"
        for key, label in TAB_LABELS
    ]
    tabs = st.tabs(labels_with_marks)
    #Llamando tabs.
    process_assessment_tab(
        tab            = tabs[0],
        player_id      = st.session_state.selected_player_id,
        coach_id       = st.session_state.selected_coach_id,
        program_id     = st.session_state.selected_program_id,
        items     = items_core,
        category  = "Core Values",
        tab_key   = "core",
        slider_max=10,
        slider_default=5,
        evaluation_date   = eval_date
    )
    with tabs[0]:
        checked = "core" in st.session_state.completed_tabs
        new_val = st.checkbox(
            "Mark 'Core Values' complete",
            value=checked,
            key="chk_core"
        )
        if new_val and not checked:
            st.session_state.completed_tabs.add("core")
        elif not new_val and checked:
            st.session_state.completed_tabs.discard("core")

    #Resto de tabs
    for idx, (key, label) in enumerate(TAB_LABELS[1:], start=1):
        raw_items = RAW_SPECS[key]
        list_items = [{"item": it, "core_value_id": None, "category": label} for it in raw_items]
        process_assessment_tab(
            tabs[idx],
            st.session_state.selected_player_id,
            st.session_state.selected_coach_id,
            st.session_state.selected_program_id,
            list_items,
            label,
            key,
            slider_max= 10,
            slider_default=5,
            evaluation_date   = eval_date,
        )
        with tabs[idx]:
            checked = key in st.session_state.completed_tabs
            new_val = st.checkbox(
                f"Mark '{label}' complete",
                value   = checked,
                key     = f"chk_{key}"
            )

            #si cambió, actualizamos completed_tabs
            if new_val and not checked:
                st.session_state.completed_tabs.add(key)
            elif not new_val and checked:
                st.session_state.completed_tabs.discard(key)

    delete_batch = st.session_state.delete_batch
    is_deleting = bool(delete_batch)
    is_editing  = bool(st.session_state.edit_batch)
    all_checked = len(st.session_state.completed_tabs) == len(TAB_LABELS)

    if is_deleting:
        btn_label = "Delete All"
    elif is_editing:
        btn_label = "Update All"
    elif all_checked:
        btn_label = "Finish & Save New Evaluation"
    else:
        btn_label = "Save All"

    #Global save/update callback
    def _on_global_click():
        now   = datetime.now()
        pid   = st.session_state.selected_player_id
        cid   = st.session_state.selected_coach_id
        prog  = st.session_state.selected_program_id
        delete_batch = st.session_state.delete_batch
        is_editing   = bool(st.session_state.edit_batch)

        # modo delete, borramos SOLO esos batches y reiniciamos
        if delete_batch:
            with SessionLocal() as db:
                for ts in delete_batch.values():
                    db.query(PlayerAssessments) \
                    .filter(
                        PlayerAssessments.player_id    == pid,
                        PlayerAssessments.coach_id     == cid,
                        PlayerAssessments.program_id   == prog,
                        PlayerAssessments.created_at   == ts
                    ).delete(synchronize_session=False)
                db.commit()
            st.success("Deleted successfully")
            st.session_state.delete_batch.clear()
            st.session_state.completed_tabs.clear()
            st.session_state.last_player_id = None
            return

        # Si estamos editando, borramos el batch anterior
        if is_editing:
            with SessionLocal() as db:
                for ts in st.session_state.edit_batch.values():
                    db.query(PlayerAssessments) \
                    .filter(
                        PlayerAssessments.player_id    == pid,
                        PlayerAssessments.coach_id     == cid,
                        PlayerAssessments.program_id   == prog,
                        PlayerAssessments.created_at   == ts
                    ).delete(synchronize_session=False)
                db.commit()
            st.session_state.edit_batch.clear()


        #Insertar/actualizar lote completo
        #     Recorremos cada pestaña (core + las demás) y levantamos sliders + notas
        new_records = []
        for key, label in TAB_LABELS:
            # armamos la lista de ítems según la pestaña
            if key == "core":
                bloc = items_core
            else:
                bloc = [
                    {"item": it, "category": label, "core_value_id": None}
                    for it in RAW_SPECS[key]
                    ]

            notes = st.session_state.get(f"notes_{key}", "")
            for idx, it in enumerate(bloc):
                val = st.session_state[f"{key}_slider_{idx}"]
                new_records.append(
                    PlayerAssessments(
                        player_id     = pid,
                        coach_id      = cid,
                        program_id    = prog,
                        category      = it["category"],
                        item          = it["item"],
                        value         = val,
                        notes         = notes,
                        core_value_id = it.get("core_value_id"),
                        created_at    = now
                    )
                )

        with SessionLocal() as db:
            db.add_all(new_records)
            db.commit()

        st.success("Saved/Updated successfully")
        # Finalmente, refrescamos flags y forzamos a re-seleccionar jugador
        st.session_state.completed_tabs.clear()
        st.session_state.last_player_id = None
        
    # 3) Renderizar botón global
    st.button(
        label    = btn_label,
        disabled = not (is_deleting or all_checked),
        key      = "btn_global",
        on_click = _on_global_click
    )

def main():
    show_filters()
if __name__ == "__main__":
    main()