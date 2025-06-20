import streamlit as st
from utils.taka import api_taka, auth_taka
from utils import util

util.setup_page("Taka")

# LOGIN + MENU
util.login_if_needed()


st.header(":blue[Taka] Evaluation", divider=True)


# Mostrar login de Taka
auth_taka.generarLogin()

# Verificamos si se hizo login correctamente
if "auth_token" not in st.session_state or "cookies" not in st.session_state or "usuario" not in st.session_state:
    st.stop()  # Se detiene hasta que se haga login correctamente

# Si estamos logueados:
st.header('Videos disponibles en tus partidos - Taka.io')

# Recuperamos valores
token = st.session_state["auth_token"]
cookies = st.session_state["cookies"]
user = st.session_state["usuario"]

# Mostramos información del usuario
first = user.get("firstName", "SinNombre")
last = user.get("lastName", "SinApellido")
st.markdown(f" Usuario: {first} {last}")

# Como no tenemos `club.name` ni `defaultTeams` en el login, los omitimos por ahora
# Si esos campos no están, puedes comentarlos temporalmente o mostrar mensaje
if "club" in user and user["club"]:
    st.markdown(f" Club principal: {user['club']['name']} (ID: {user['club']['id']})")
else:
    st.warning("⚠️ Este usuario no tiene club principal definido.")

# Si se quiere seguir usando get_user_clubs() para obtener equipos, puedes dejar esta parte:
response = api_taka.get_user_clubs(token, cookies)

if not response or "data" not in response or not response["data"].get("me"):
    st.warning("No se pudieron obtener equipos desde `get_user_clubs`. Mostrando solo login.")
    st.stop()

user = response["data"]["me"]

# Mostrar equipos por categoría
teams = user.get("defaultTeams", [])
if not teams:
    st.warning("Este usuario no tiene equipos asignados.")
    st.stop()

team = st.selectbox("Elige equipo", [t["name"] for t in teams])

# Obtener ID del equipo seleccionado
selected_team = next(t for t in teams if t["name"] == team)
team_id = selected_team["id"]
category_id = selected_team["info"]["category"]["id"]

st.write(f"Team ID: {team_id} |  Category ID: {category_id}")
