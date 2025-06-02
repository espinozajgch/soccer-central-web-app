import requests
import streamlit as st

API_URL = "https://api.taka.io/proscore"

HEADERS = {
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://taka.io',
    'referer': 'https://taka.io/',
    'user-agent': 'Mozilla/5.0'
}

def generarLogin():
    st.subheader(" Login en Taka")
    email = st.text_input("Email", value="davidkenneysoccer@gmail.com")
    password = st.text_input("Password", type="password", value="SoccerBall123!")

    if st.button("Iniciar sesión"):
        user, token, cookies = login(email, password)
        if token and user:
            st.success("Login exitoso")
            st.session_state["auth_token"] = token
            st.session_state["cookies"] = cookies
            st.session_state["usuario"] = user  # Guardamos todo el usuario ya logueado
        else:
            st.error("Error en el login")

def login(email, password):
    body = {
        "operationName": "authBasic",
        "variables": {
            "input": {
                "email": email,
                "password": password,
                "rememberMe": False
            }
        },
        "query": """
        mutation authBasic($input: AuthBasicInput!) {
          authBasic(input: $input) {
            user {
              id
              firstName
              lastName
              email
              username
              roles
            }
            __typename
          }
        }
        """
    }
    response = requests.post(API_URL, json=body, headers=HEADERS)
    if response.status_code == 200:
        token = response.cookies.get('auth_token')
        cookies = response.cookies.get_dict()
        data = response.json()
        user = data.get("data", {}).get("authBasic", {}).get("user")
        return user, token, cookies
    return None, None, None
