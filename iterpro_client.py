import os
import requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
AUTH_HEADER = os.getenv("AUTH_HEADER")

# Para llamar a iterpro https://api.iterpro.com/api/v1/players
def get_players():
    url = f"{BASE_URL}/players"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("[DEBUG] URL:", url)
    print("[DEBUG] HEADERS:", headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Para obtener detalles de un jugador específico
def get_player_by_id(player_id):
    url = f"{BASE_URL}/players/{player_id}"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("[DEBUG] Player Details URL:", url)
    print("[DEBUG] Player Details HEADERS:", headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()