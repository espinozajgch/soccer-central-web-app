from flask import Flask, render_template, jsonify
from iterpro_client import get_players

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

if __name__ == "__main__":
    app.run(debug=True)
