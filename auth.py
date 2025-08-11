import json
from functools import wraps
from flask import session, redirect, url_for, flash

def load_users():
    """Load users from JSON file"""
    try:
        with open('users.json', 'r') as f:
            data = json.load(f)
            return data.get('users', [])
    except FileNotFoundError:
        return []

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """Decorator to require specific roles for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            
            user_role = session['user']['role']
            if user_role not in allowed_roles:
                flash('Access denied. You do not have permission to view this page.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_team_players(team_id):
    """Get players for a specific team"""
    from iterpro_client import get_players_by_team
    try:
        return get_players_by_team(team_id)
    except Exception as e:
        print(f"[DEBUG] Error getting team players: {str(e)}")
        return []

def get_user_player_profile(player_id):
    """Get specific player profile"""
    from iterpro_client import get_player_by_id
    try:
        return get_player_by_id(player_id)
    except Exception as e:
        print(f"[DEBUG] Error getting player profile: {str(e)}")
        return None
