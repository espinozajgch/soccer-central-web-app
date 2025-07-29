from flask import Flask, render_template, jsonify, request
from iterpro_client import get_players, get_player_by_id

app = Flask(__name__, template_folder="templates", static_folder="static")

# Para cargar la pagina inicial
@app.route("/")
def index():
    try:
        players = get_players()
        return render_template("index.html", players=players)
    except Exception as e:
        return render_template("index.html", players=[], error=str(e))

# Para llamar a iterpro https://api.iterpro.com/api/v1/players
@app.route("/players")
def get_players_function():
    try:
        return jsonify(get_players())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para obtener detalles de un jugador específico
@app.route("/players/<player_id>")
def get_player_details(player_id):
    try:
        player = get_player_by_id(player_id)
        return jsonify(player)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para mostrar la página de detalles del jugador
@app.route("/player")
def player_details_page():
    return render_template("player_details.html")

if __name__ == "__main__":
    app.run(debug=True)
