import streamlit as st
from sqlalchemy.orm import joinedload
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

# ---------------------------------------------------------------------------------
# Init flags & sesion state.
if "inited" not in st.session_state:
    st.session_state["completed_tabs"] = set()
    st.session_state["edit_mode"]     = False
    st.session_state["delete_mode"]   = False
    st.session_state["ts_to_delete"]  = None
    st.session_state["ts_to_edit"]    = None
    st.session_state["last_player_id"] = None
    st.session_state["inited"]        = True
# ---------------------------------------------------------------------------------
ALL_TABS = {"core", "tech", "tac", "phys", "match", "lead"}
TAB_LABELS = [
    ("core",  "Core Values"),
    ("tech",  "Technical Skills"),
    ("tac",   "Tactical Understanding"),
    ("phys",  "Physical Performance"),
    ("match", "Match Performance"),
    ("lead",  "Leadership & Character")
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
@st.cache_resource
def load_core_items():
    with SessionLocal() as session:
        vals = session.query(CoreValue).all()
    return [
        {"item": cv.name, "core_value_id": cv.id, "category": f"Core Value {i+1}"}
        for i, cv in enumerate(vals)
    ]
# --------------------------------------------------------------------------------------------------
def show_filters():
    init_core_values_and_programs()
    st.session_state.setdefault("completed_tabs", set())
    st.session_state.setdefault("edit_mode", False)
    st.session_state.setdefault("delete_mode", False)
    st.session_state.setdefault("ts_to_delete", None)
    st.session_state.setdefault("ts_to_edit",   None)

    with SessionLocal() as session:
        players   = (
            session.query(Players)
                   .join(Players.user)
                   .options(joinedload(Players.user))
                   .filter(Users.role_id == 4)
                   .all()
        )
        #core_vals = session.query(CoreValue).all()
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
    #Enh. player selection.
    with st.form("filters_form"):
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 1])
        with col1:
            selected_player_idx = st.selectbox(
                "Player",
                options=range(len(players)),
                format_func=lambda i: player_labels[i]
            )
        with col2:
            selected_coach_name = st.selectbox(
                "Coach",
                coach_labels
            )
        with col3:
            selected_program_name = st.selectbox(
                "Program",
                program_labels
            )
        with col4:
            selected_date = st.date_input(
                "Evaluation Date",
                value=date.today()
            )
        with col5:
            apply_filters = st.form_submit_button(
                "Apply Filters", 
                use_container_width=True
            )

    if apply_filters:
        st.session_state.selected_player_index = selected_player_idx
        st.session_state.selected_player_id    = players[selected_player_idx].player_id
        st.session_state.selected_coach_name   = selected_coach_name
        st.session_state.selected_coach_id     = coach_map[selected_coach_name]
        st.session_state.selected_program_name = selected_program_name
        st.session_state.selected_program_id   = program_map.get(selected_program_name)
        st.session_state.evaluation_date       = selected_date

        new_pid  = st.session_state.selected_player_id
        if st.session_state.last_player_id  != new_pid:
            st.session_state.edit_mode      = False
            st.session_state.delete_mode    = False
            st.session_state.ts_to_delete   = None
            st.session_state.ts_to_edit     = None
            st.session_state.completed_tabs = set()
            st.session_state.last_player_id = new_pid

    # Defaults firts load.
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
    items_core = load_core_items()
    
    last_rec = (
            session.query(PlayerAssessments.created_at)
            .filter_by(player_id=pid, coach_id=cid, program_id=prog)
            .order_by(PlayerAssessments.created_at.desc())
            .first()
        )
    last_ts = last_rec.created_at if last_rec else None
    if last_ts:
        # load saved categories
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
    col_edit, col_del, col_can = st.columns([1,1,1])
    if col_edit.button("\u270F\uFE0F Edit Last Evaluation", disabled=not last_ts):
        st.session_state.edit_mode = True
        st.session_state.delete_mode = False
        st.session_state.ts_to_edit  = last_ts
    if col_del.button("\U0001F5D1\U0000FE0F Delete Last Evaluation", disabled=not last_ts):
        st.session_state.delete_mode = True
        st.session_state.edit_mode = False
        st.session_state.ts_to_delete = last_ts    
    if col_can.button("Cancel", disabled=not last_ts):
        st.session_state.edit_mode = False
        st.session_state.delete_mode = False
        st.session_state.pop("ts_to_edit", None)
        st.session_state.pop("ts_to_delete", None)

    #Process Control Checks.
    labels_with_marks = [
        f"{'\u2705\uFE0F' if key in st.session_state.completed_tabs else ''} {label}"
        for key, label in TAB_LABELS
    ]
    tabs = st.tabs(labels_with_marks)
    with st.form(key="eval_form"):
        for idx, (key, label) in enumerate(TAB_LABELS):
            tab = tabs[idx]
            with tab:
                # determine items for this tab
                items = items_core if key == "core" else [
                    {"item": it, "category": label, "core_value_id": None}
                    for it in RAW_SPECS[key]
                ]
                # if editing, preload values; else defaults
                prev_map = {}
                if st.session_state.edit_mode:
                    with SessionLocal() as session:
                        edit_rows = session.query(PlayerAssessments)\
                            .filter_by(
                                player_id=pid, coach_id=cid,
                                program_id=prog, created_at=last_ts
                            ).all()
                    prev_map = {r.item: r for r in edit_rows}

                # sliders
                for i, it in enumerate(items):
                    sk = f"{key}_slider_{i}"
                    default = prev_map.get(it["item"], None)
                    val = default.value if default else st.session_state.get(sk, 5)
                    st.slider(it["item"], 1, 10, value=val, key=sk, help="Scale 1–10")

                # comments
                nk = f"notes_{key}"
                if nk not in st.session_state:
                    st.session_state[nk] = (prev_map.get(items[0]["item"]).notes
                                            if prev_map else "")
                st.text_area("Comments", value=st.session_state[nk],
                             key=nk, height=100)

                # checkbox complete
                checked = key in st.session_state.completed_tabs
                new_val = st.checkbox(f"Mark '{label}' complete",
                                      value=checked, key=f"chk_{key}")
                if new_val and not checked:
                    st.session_state.completed_tabs.add(key)
                elif not new_val and checked:
                    st.session_state.completed_tabs.discard(key)

        all_checked = len(st.session_state.completed_tabs) == len(TAB_LABELS)
        delete_mode = st.session_state.delete_mode
        edit_mode   = st.session_state.edit_mode
        if delete_mode:
            btn_label = "Delete Evaluation"
            btn_disabled = False
        elif edit_mode:
            btn_label = "Update Evaluation"
            btn_disabled = not all_checked
            st.session_state.edit_mode = True
        elif all_checked:
            btn_label = "Finish & Save New Evaluation"
            btn_disabled = False
        else:
            btn_label = "Save All"
            btn_disabled = True

        submitted = st.form_submit_button(
            label=btn_label,
            disabled=btn_disabled
        )

    #Global save/update
    if submitted:
        now   = datetime.now()
        # DELETE mode
        if st.session_state.delete_mode:
            ts = st.session_state.ts_to_delete
            if ts:
                with SessionLocal() as db:
                    db.query(PlayerAssessments)\
                      .filter_by(player_id=pid, coach_id=cid, program_id=prog)\
                      .filter(PlayerAssessments.created_at == ts)\
                      .delete(synchronize_session=False)
                    db.commit()
                st.success("Deleted last evaluation successfully")
            else:
                st.error("No timestamp saved to delete")
        else:
            # if edit_mode, wipe old batch first
            if st.session_state.ts_to_edit:
                ts = st.session_state.ts_to_edit
                if ts:
                    with SessionLocal() as db:
                        db.query(PlayerAssessments)\
                            .filter_by(
                                player_id  = pid,
                                coach_id   = cid,
                                program_id = prog
                            )\
                            .filter(PlayerAssessments.created_at == ts)\
                            .delete(synchronize_session=False)
                        db.commit()

            # insert new batch
            new_recs = []
            for key, label in TAB_LABELS:
                items = items_core if key == "core" else [
                    {"item": it, "category": label, "core_value_id": None}
                    for it in RAW_SPECS[key]
                ]
                notes = st.session_state[f"notes_{key}"]
                for i, it in enumerate(items):
                    val = st.session_state[f"{key}_slider_{i}"]
                    new_recs.append(PlayerAssessments(
                        player_id=pid, coach_id=cid, program_id=prog,
                        category=it["category"], item=it["item"],
                        value=val, notes=notes,
                        core_value_id=it.get("core_value_id"),
                        created_at=now
                    ))
            with SessionLocal() as db:
                db.add_all(new_recs)
                db.commit()
            msg = "Updated successfully" if st.session_state.edit_mode else "Saved successfully"
            st.success(msg)

        # reset modes & tabs
        st.session_state.edit_mode = False
        st.session_state.delete_mode = False
        st.session_state.ts_to_delete     = None
        st.session_state.ts_to_edit       = None
        st.session_state.completed_tabs.clear()


def main():
    show_filters()
if __name__ == "__main__":
    main()