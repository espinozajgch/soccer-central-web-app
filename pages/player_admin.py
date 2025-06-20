import streamlit as st
from sqlalchemy.orm import Session, joinedload
from db.models import Users, Players
from db.db import engine
from utils import util
from utils import login

util.setup_page("Player 360")

# LOGIN + MENU
util.login_if_needed()

st.header(":blue[Players] Admin", divider=True)

def edit_player_info():
    current_user = login.get_logged_in_user()

    # 🚫 Restringir acceso a admin
    if not current_user or current_user.role_id != 1:
        st.error("Access denied. Only admin users can access this page.")
        return

    st.text("🛠️ Edit Player Info")

    with Session(engine) as session:
        # Obtener todos los jugadores
        players = session.query(Players).options(joinedload(Players.user)).join(Users).order_by(Users.last_name).all()
        player_options = [f"{p.user.first_name} {p.user.last_name} (ID: {p.player_id})" for p in players]
        selected = st.selectbox("Select Player", player_options)

        selected_player = players[player_options.index(selected)]
        selected_user = selected_player.user

        with st.form("edit_player_form"):
            st.subheader("Edit Personal Info")
            first_name = st.text_input("First Name", value=selected_user.first_name)
            last_name = st.text_input("Last Name", value=selected_user.last_name)
            email = st.text_input("Email", value=selected_user.email or "")
            phone = st.text_input("Phone", value=selected_user.phone or "")
            country = st.text_input("Country", value=selected_user.country or "")

            st.subheader("Edit Player Info")
            number = st.number_input("Jersey Number", value=selected_player.number or 0)
            primary_position = st.text_input("Primary Position", value=selected_player.primary_position or "")
            secondary_position = st.text_input("Secondary Position", value=selected_player.secondary_position or "")
            dominant_foot = st.selectbox("Dominant Foot", ["Right", "Left", "Both", "Unknown"], index=["Right", "Left", "Both", "Unknown"].index(selected_player.dominant_foot or "Right"))
            height = st.number_input("Height (cm)", value=float(selected_player.height or 170), step=1.0)

            submitted = st.form_submit_button("💾 Save Changes")

        if submitted:
            try:
                # Actualizar usuario
                selected_user.first_name = first_name
                selected_user.last_name = last_name
                selected_user.email = email
                selected_user.phone = phone
                selected_user.country = country

                # Actualizar jugador
                selected_player.number = number
                selected_player.primary_position = primary_position
                selected_player.secondary_position = secondary_position
                selected_player.dominant_foot = dominant_foot
                selected_player.height = height

                session.commit()
                st.success("Player information updated successfully!")

            except Exception as e:
                session.rollback()
                st.error(f"An error occurred: {e}")
def main():
    edit_player_info()

if __name__ == "__main__":
    main()