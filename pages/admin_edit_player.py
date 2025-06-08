import streamlit as st
from sqlalchemy.orm import Session
from models import Users, Players
from db import engine
from utils import login


def Setup_page():
    login.generarLogin()
    # Configuración de la página
    # Configuración título de página.
    # st.set_page_config(page_title="Player Layout Draft", page_icon=":soccer:",
    #                    layout="centered",initial_sidebar_state="auto",
    #                    menu_items={
    #                        'Get Help': 'https://soccercentralsa.byga.net',
    #                        'About': """
    #                             ## Acerca de la Aplicación

    #                             **Soccer Central Web App** es una aplicación desarrollada para facilitar el análisis del rendimiento deportivo de los jugadores de la academia Soccer Central.

    #                             - **Desarrollado con:** Streamlit
    #                             - **Versión:** 1.0
    #                             - **Contacto:** support@soccercentral.com
    #                             """
    #                         }
    #                    )
    # Definición de Título y Descripción de Página
    # Creación del Look and Feel de la Página
    logo = "./assets/images/soccer-central.png"
    st.sidebar.image(logo, width=350)

    # ******************************************Feature Provisional para Demo**************************************************************
    # En el sidebar, el usuario selecciona los colores de fondo para cada panel
    main_bg_color = st.sidebar.color_picker("**Choose Background Color for Principal Panel**", "#EDF4F5")
    sidebar_bg_color = st.sidebar.color_picker("**Choose Background Color for Sidebar Panel**", "#D0DEE2")
    # Inyectando CSS para personalizar los fondos utilizando los colores seleccionados
    st.markdown(
        f"""
        <style>
        /* Contenedor principal */
        [data-testid="stAppViewContainer"] {{
            background-color: {main_bg_color};

        }}
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    # **************************************FIN de Feature Provisional para Demo***********************************************************


def Edit_Player_Info():
    current_user = login.get_logged_in_user()

    # 🚫 Restringir acceso a admin
    if not current_user or current_user.role_id != 1:
        st.error("Access denied. Only admin users can access this page.")
        return

    st.title("🛠️ Edit Player Info")

    with Session(engine) as session:
        # Obtener todos los jugadores
        players = session.query(Players).join(Users).order_by(Users.last_name).all()
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
            dominant_foot = st.selectbox("Dominant Foot", ["Right", "Left", "Both"], index=["Right", "Left", "Both"].index(selected_player.dominant_foot or "Right"))
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
    Setup_page()
    Edit_Player_Info()

if __name__ == "__main__":
    main()