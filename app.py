from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from iterpro_client import get_players, get_player_by_id, get_team_by_id, get_teams, get_cache_stats, clear_team_cache, clear_player_cache, clear_cache, cleanup_expired_cache
from auth import authenticate_user, login_required, role_required, get_user_team_players, get_user_player_profile

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = 'your-secret-key-change-this-in-production'

# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            session['user'] = user
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# Para cargar la pagina inicial
@app.route("/")
@login_required
def index():
    try:
        user = session.get('user')
        
        if user['role'] == 'admin':
            # Admin can see all players
            players = get_players()
        elif user['role'] == 'coach':
            # Coach can see their team players
            players = get_user_team_players(user.get('team_id'))
        elif user['role'] == 'player':
            # Player can only see their own profile
            player_profile = get_user_player_profile(user.get('player_id'))
            players = [player_profile] if player_profile else []
        else:
            players = []
            
        return render_template("index.html", players=players)
    except Exception as e:
        return render_template("index.html", players=[], error=str(e))

# Para llamar a iterpro https://api.iterpro.com/api/v1/players
@app.route("/players")
@login_required
def get_players_function():
    try:
        user = session.get('user')
        
        if user['role'] == 'admin':
            # Admin can see all players
            players = get_players()
        elif user['role'] == 'coach':
            # Coach can see their team players
            players = get_user_team_players(user.get('team_id'))
        else:
            # Player can only see their own profile
            player_profile = get_player_by_id(user.get('player_id'))
            players = [player_profile] if player_profile else []
            
        return jsonify(players)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para obtener detalles de un jugador específico
@app.route("/players/<player_id>")
@login_required
def get_player_details(player_id):
    try:
        user = session.get('user')
        
        # Check access permissions
        if user['role'] == 'admin':
            # Admin can access any player
            pass
        elif user['role'] == 'coach':
            # Coach can access players from their team
            # This would need proper team validation in a real implementation
            pass
        elif user['role'] == 'player':
            # Player can only access their own profile
            if user.get('player_id') != player_id:
                return jsonify({"error": "Access denied"}), 403
        
        player = get_player_by_id(player_id)
        return jsonify(player)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para obtener información de equipos
@app.route("/teams")
@login_required
def get_teams_function():
    try:
        teams = get_teams()
        return jsonify(teams)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para obtener información de un equipo específico
@app.route("/teams/<team_id>")
@login_required
def get_team_details(team_id):
    try:
        user = session.get('user')
        
        # Check access permissions
        if user['role'] == 'admin':
            # Admin can access any team
            pass
        elif user['role'] == 'coach':
            # Coach can only access their own team
            if user.get('team_id') != team_id:
                return jsonify({"error": "Access denied"}), 403
        elif user['role'] == 'player':
            # Player can only access their own team
            if user.get('team_id') != team_id:
                return jsonify({"error": "Access denied"}), 403
        
        team = get_team_by_id(team_id)
        if team:
            return jsonify(team)
        else:
            return jsonify({"error": "Team not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para mostrar la página de detalles del jugador
@app.route("/player")
@login_required
def player_details_page():
    return render_template("player_details.html")

# Cache management endpoints (for debugging)
@app.route("/cache/stats")
@login_required
def cache_stats():
    """Get cache statistics"""
    try:
        stats = get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cache/clear")
@login_required
def cache_clear():
    """Clear all cache"""
    try:
        clear_cache()
        return jsonify({"message": "All cache cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cache/clear/teams")
@login_required
def cache_clear_teams():
    """Clear team cache only"""
    try:
        clear_team_cache()
        return jsonify({"message": "Team cache cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cache/clear/players")
@login_required
def cache_clear_players():
    """Clear player cache only"""
    try:
        clear_player_cache()
        return jsonify({"message": "Player cache cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cache/cleanup")
@login_required
def cache_cleanup():
    """Clean up expired cache files"""
    try:
        removed_count = cleanup_expired_cache()
        return jsonify({"message": f"Cleaned up {removed_count} expired cache files"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
