import os
import requests
import json
import tempfile
from dotenv import load_dotenv
from pathlib import Path
import time
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
AUTH_HEADER = os.getenv("AUTH_HEADER")

# Cache configuration
_cache_expiration = 300  # 5 minutes in seconds
_cache_dir = Path(tempfile.gettempdir()) / "soccer_central_cache"
_cache_dir.mkdir(exist_ok=True)

def _get_cache_file_path(cache_type, key):
    """Get the file path for a cache entry"""
    safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
    return _cache_dir / f"{cache_type}_{safe_key}.json"

def _load_cache_entry(file_path):
    """Load a cache entry from file"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
                if time.time() - cache_entry['timestamp'] < _cache_expiration:
                    return cache_entry['data']
                else:
                    # Cache expired, remove file
                    file_path.unlink()
                    print(f"[DEBUG] Cache expired for {file_path.name}")
    except Exception as e:
        print(f"[DEBUG] Error loading cache from {file_path}: {e}")
    return None

def _save_cache_entry(file_path, data):
    """Save a cache entry to file"""
    try:
        cache_entry = {
            'data': data,
            'timestamp': time.time()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cache_entry, f, ensure_ascii=False, indent=2)
        print(f"[DEBUG] Cached data to {file_path.name}")
    except Exception as e:
        print(f"[DEBUG] Error saving cache to {file_path}: {e}")

def _get_cached_team(team_id):
    """Get team from cache if it exists and is not expired"""
    file_path = _get_cache_file_path('team', team_id)
    cached_data = _load_cache_entry(file_path)
    if cached_data:
        print(f"[DEBUG] Using cached team data for {team_id}")
    return cached_data

def _cache_team(team_id, team_data):
    """Cache team data with timestamp"""
    file_path = _get_cache_file_path('team', team_id)
    _save_cache_entry(file_path, team_data)

def _get_cached_players():
    """Get players from cache if they exist and are not expired"""
    file_path = _get_cache_file_path('players', 'all_players')
    cached_data = _load_cache_entry(file_path)
    if cached_data:
        print(f"[DEBUG] Using cached players data")
    return cached_data

def _cache_players(players_data):
    """Cache players data with timestamp"""
    file_path = _get_cache_file_path('players', 'all_players')
    _save_cache_entry(file_path, players_data)

def _get_cached_player(player_id):
    """Get individual player from cache if it exists and is not expired"""
    file_path = _get_cache_file_path('player', player_id)
    cached_data = _load_cache_entry(file_path)
    if cached_data:
        print(f"[DEBUG] Using cached player data for {player_id}")
    return cached_data

def _cache_player(player_id, player_data):
    """Cache individual player data with timestamp"""
    file_path = _get_cache_file_path('player', player_id)
    _save_cache_entry(file_path, player_data)

def clear_cache():
    """Clear all cached data"""
    try:
        for cache_file in _cache_dir.glob("*.json"):
            cache_file.unlink()
        print(f"[DEBUG] All cache cleared from {_cache_dir}")
    except Exception as e:
        print(f"[DEBUG] Error clearing cache: {e}")

def clear_team_cache():
    """Clear all cached team data"""
    try:
        team_files = list(_cache_dir.glob("team_*.json"))
        for cache_file in team_files:
            cache_file.unlink()
        print(f"[DEBUG] Team cache cleared ({len(team_files)} files)")
    except Exception as e:
        print(f"[DEBUG] Error clearing team cache: {e}")

def clear_player_cache():
    """Clear all cached player data"""
    try:
        player_files = list(_cache_dir.glob("player_*.json"))
        players_list_files = list(_cache_dir.glob("players_*.json"))
        all_player_files = player_files + players_list_files
        for cache_file in all_player_files:
            cache_file.unlink()
        print(f"[DEBUG] Player cache cleared ({len(all_player_files)} files)")
    except Exception as e:
        print(f"[DEBUG] Error clearing player cache: {e}")

def cleanup_expired_cache():
    """Remove expired cache files"""
    current_time = time.time()
    removed_count = 0
    
    for cache_file in _cache_dir.glob("*.json"):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
                if current_time - cache_entry['timestamp'] >= _cache_expiration:
                    cache_file.unlink()
                    removed_count += 1
        except Exception:
            # If file is corrupted, remove it
            cache_file.unlink()
            removed_count += 1
    
    if removed_count > 0:
        print(f"[DEBUG] Cleaned up {removed_count} expired cache files")
    return removed_count

def get_cache_stats():
    """Get cache statistics"""
    current_time = time.time()
    team_valid_entries = 0
    team_expired_entries = 0
    player_valid_entries = 0
    player_expired_entries = 0
    players_list_valid = 0
    players_list_expired = 0
    
    # Count team cache files
    for cache_file in _cache_dir.glob("team_*.json"):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
                if current_time - cache_entry['timestamp'] < _cache_expiration:
                    team_valid_entries += 1
                else:
                    team_expired_entries += 1
        except Exception:
            team_expired_entries += 1
    
    # Count individual player cache files
    for cache_file in _cache_dir.glob("player_*.json"):
        if "players_all_players" in cache_file.name:
            continue  # Skip the players list file
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
                if current_time - cache_entry['timestamp'] < _cache_expiration:
                    player_valid_entries += 1
                else:
                    player_expired_entries += 1
        except Exception:
            player_expired_entries += 1
    
    # Count players list cache file
    players_list_file = _get_cache_file_path('players', 'all_players')
    if players_list_file.exists():
        try:
            with open(players_list_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
                if current_time - cache_entry['timestamp'] < _cache_expiration:
                    players_list_valid = 1
                else:
                    players_list_expired = 1
        except Exception:
            players_list_expired = 1
    
    total_files = len(list(_cache_dir.glob("*.json")))
    
    return {
        'cache_directory': str(_cache_dir),
        'teams': {
            'total_entries': team_valid_entries + team_expired_entries,
            'valid_entries': team_valid_entries,
            'expired_entries': team_expired_entries,
        },
        'players': {
            'total_entries': player_valid_entries + player_expired_entries,
            'valid_entries': player_valid_entries,
            'expired_entries': player_expired_entries,
        },
        'players_list': {
            'total_entries': players_list_valid + players_list_expired,
            'valid_entries': players_list_valid,
            'expired_entries': players_list_expired,
        },
        'total_cache_files': total_files
    }

# Para llamar a iterpro https://api.iterpro.com/api/v1/players
def get_players():
    # Check cache first
    cached_players = _get_cached_players()
    if cached_players:
        return cached_players
    
    url = f"{BASE_URL}/players"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("[DEBUG] URL:", url)
    print("[DEBUG] HEADERS:", headers)

    try:
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] Players response status: {response.status_code}")
        print(f"[DEBUG] Players response content: {response.text[:500]}...")
        response.raise_for_status()
        players_data = response.json()
        print(f"[DEBUG] Players data count: {len(players_data) if isinstance(players_data, list) else 'N/A'}")
        
        # Cache the players data
        _cache_players(players_data)
        
        return players_data
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting players: {str(e)}")
        return []

# Para obtener detalles de un jugador específico
def get_player_by_id(player_id):
    # Check cache first
    cached_player = _get_cached_player(player_id)
    if cached_player:
        return cached_player
    
    url = f"{BASE_URL}/players/{player_id}"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("[DEBUG] Player Details URL:", url)
    print("[DEBUG] Player Details HEADERS:", headers)

    try:
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] Player response status: {response.status_code}")
        print(f"[DEBUG] Player response content: {response.text[:500]}...")
        response.raise_for_status()
        player_data = response.json()
        print(f"[DEBUG] Player data: {player_data.get('displayName', 'N/A') if player_data else 'N/A'}")
        
        # Cache the player data
        _cache_player(player_id, player_data)
        
        return player_data
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting player details: {str(e)}")
        return None

# Para obtener información de un equipo específico
def get_team_by_id(team_id):
    # Check cache first
    cached_team = _get_cached_team(team_id)
    if cached_team:
        return cached_team
    
    url = f"{BASE_URL}/teams/{team_id}"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("[DEBUG] Team Details URL:", url)
    print("[DEBUG] Team Details HEADERS:", headers)

    try:
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] Team response status: {response.status_code}")
        print(f"[DEBUG] Team response content: {response.text[:500]}...")
        response.raise_for_status()
        team_data = response.json()
        print(f"[DEBUG] Team data: {team_data}")
        
        # Cache the team data
        _cache_team(team_id, team_data)
        
        return team_data
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting team details: {str(e)}")
        return None

# Para obtener todos los equipos
def get_teams():
    # Check cache for all teams
    cached_teams = _get_cached_team('all_teams')
    if cached_teams:
        return cached_teams
    
    url = f"{BASE_URL}/teams"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("[DEBUG] Teams URL:", url)
    print("[DEBUG] Teams HEADERS:", headers)

    try:
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] Teams response status: {response.status_code}")
        print(f"[DEBUG] Teams response content: {response.text[:500]}...")
        response.raise_for_status()
        teams_data = response.json()
        print(f"[DEBUG] Teams data: {teams_data}")
        
        # Cache all teams data
        _cache_team('all_teams', teams_data)
        
        # Also cache individual teams for faster access
        if isinstance(teams_data, list):
            for team in teams_data:
                if '_id' in team:
                    _cache_team(team['_id'], team)
        
        return teams_data
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting teams: {str(e)}")
        return []

# Para obtener jugadores de un equipo específico
def get_players_by_team(team_id):
    """Get all players and filter by team ID"""
    try:
        all_players = get_players()
        team_players = [player for player in all_players if player.get('teamId') == team_id]
        print(f"[DEBUG] Team ID: {team_id}, Total players: {len(all_players)}, Team players: {len(team_players)}")
        return team_players
    except Exception as e:
        print(f"[DEBUG] Error getting team players: {str(e)}")
        return []