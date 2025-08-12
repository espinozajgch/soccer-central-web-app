import os
import requests
import json
import tempfile
from dotenv import load_dotenv
from pathlib import Path
import time
import random
import numpy as np
from datetime import datetime, timedelta
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

def get_player_test_instances(player_id):
    """Get test instances for a specific player"""
    url = f"{BASE_URL}/players/{player_id}/test-instances"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting player test instances: {str(e)}")
        return []

def get_player_test_instances_batch(player_ids, max_players=10):
    """
    Fetch test instances for multiple players efficiently
    Limit to max_players to avoid overwhelming the API
    """
    try:
        all_test_data = {}
        
        # Limit the number of players to avoid API overload
        limited_player_ids = player_ids[:max_players]
        
        print(f"[DEBUG] Fetching test instances for {len(limited_player_ids)} players")
        
        for player_id in limited_player_ids:
            try:
                test_instances = get_player_test_instances(player_id)
                if test_instances:
                    all_test_data[player_id] = test_instances
                    print(f"[DEBUG] Got {len(test_instances)} test instances for player {player_id}")
                else:
                    print(f"[DEBUG] No test instances for player {player_id}")
            except Exception as e:
                print(f"Error fetching test instances for player {player_id}: {e}")
                continue
        
        print(f"[DEBUG] Total players with test data: {len(all_test_data)}")
        return all_test_data
        
    except Exception as e:
        print(f"Error in get_player_test_instances_batch: {e}")
        return {}

def extract_latest_test_value(test_instances, test_name):
    """
    Extract the latest test value for a specific test name from test instances
    """
    try:
        if not test_instances:
            return None
        
        print(f"[DEBUG] Looking for test '{test_name}' in {len(test_instances)} instances")
        matching_instances = []
        
        for instance in test_instances:
            instance_test_name = instance.get('testName', '')
            
            # Check if test names match (allowing for variations)
            if (test_name.lower() in instance_test_name.lower() or 
                instance_test_name.lower() in test_name.lower()):
                
                print(f"[DEBUG] Found match! Test name: '{instance_test_name}'")
                results = instance.get('results', {})
                if results and 'rawValue' in results:
                    raw_value = results.get('rawValue')
                    date = instance.get('date', '')
                    
                    if raw_value is not None and date:
                        matching_instances.append({
                            'value': raw_value,
                            'date': date
                        })
                        print(f"[DEBUG] Added value: {raw_value} from date: {date}")
        
        if matching_instances:
            # Sort by date and get the latest
            latest_instance = max(matching_instances, key=lambda x: x.get('date', ''))
            print(f"[DEBUG] Returning latest value: {latest_instance.get('value')}")
            return latest_instance.get('value')
        
        print(f"[DEBUG] No matching instances found for '{test_name}'")
        return None
        
    except Exception as e:
        print(f"Error extracting latest test value for {test_name}: {e}")
        return None

def get_player_thresholds(player_id):
    """Get thresholds for a specific player"""
    url = f"{BASE_URL}/players/{player_id}/thresholds"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting player thresholds: {str(e)}")
        return []

def get_team_thresholds(team_id):
    """Get thresholds for a specific team"""
    url = f"{BASE_URL}/teams/{team_id}/thresholds"
    headers = {
        "Authorization": AUTH_HEADER,
        "x-iterpro-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error getting team thresholds: {str(e)}")
        return []

def generate_historical_data(current_value, test_name, num_entries=10):
    """Generate historical data with normal distribution for a test"""
    # Define test-specific parameters
    test_configs = {
        # Anthropometry
        "Height": {"unit": "cm", "std_dev": 2.0, "is_integer": False},
        "Weight": {"unit": "kg", "std_dev": 3.0, "is_integer": False},
        "BMI": {"unit": "", "std_dev": 1.5, "is_integer": False},
        "% BF": {"unit": "%", "std_dev": 2.0, "is_integer": False},
        
        # Power
        "Single Leg Jump": {"unit": "%", "std_dev": 3.0, "is_integer": False},
        "CMJ Arm Swing HT": {"unit": "cm", "std_dev": 4.0, "is_integer": False},
        "CMJ Arm Locked HT": {"unit": "cm", "std_dev": 3.5, "is_integer": False},
        "Diff % Height Swing-Locked": {"unit": "%", "std_dev": 2.5, "is_integer": False},
        
        # Speed
        "5m": {"unit": "s", "std_dev": 0.2, "is_integer": False},
        "10m": {"unit": "s", "std_dev": 0.3, "is_integer": False},
        "20m": {"unit": "s", "std_dev": 0.4, "is_integer": False},
        "30m": {"unit": "s", "std_dev": 0.5, "is_integer": False},
        
        # Agility
        "T Test": {"unit": "s", "std_dev": 0.8, "is_integer": False},
        "Illinois": {"unit": "s", "std_dev": 1.0, "is_integer": False},
        "ArrowHead": {"unit": "s", "std_dev": 1.2, "is_integer": False},
        
        # Endurance
        "Lactate": {"unit": "mmol/L", "std_dev": 0.8, "is_integer": False},
        "YYIRT1": {"unit": "m", "std_dev": 200, "is_integer": True},
        "YYIRT2": {"unit": "m", "std_dev": 150, "is_integer": True}
    }
    
    config = test_configs.get(test_name, {"unit": "", "std_dev": 2.0, "is_integer": False})
    
    # Generate dates (last 10 measurements, 2-4 weeks apart)
    dates = []
    current_date = datetime.now()
    for i in range(num_entries):
        days_back = random.randint(14, 28) * (i + 1)  # 2-4 weeks apart
        date = current_date - timedelta(days=days_back)
        dates.append(date.strftime("%Y-%m-%d"))
    
    # Generate values with normal distribution
    values = []
    for i in range(num_entries):
        if i == 0:  # Latest measurement (real data)
            values.append({
                "value": current_value,
                "date": dates[i],
                "is_real": True
            })
        else:  # Historical data (generated)
            # Use normal distribution with low standard deviation
            generated_value = np.random.normal(current_value, config["std_dev"])
            
            # Ensure reasonable bounds
            if test_name in ["Height", "Weight", "BMI", "% BF"]:
                generated_value = max(0, generated_value)
            elif test_name in ["5m", "10m", "20m", "30m", "T Test", "Illinois", "ArrowHead"]:
                generated_value = max(0.5, generated_value)  # Minimum reasonable time
            elif test_name in ["YYIRT1", "YYIRT2"]:
                generated_value = max(0, generated_value)
            
            # Round to integer if needed
            if config["is_integer"]:
                generated_value = int(round(generated_value))
            
            values.append({
                "value": generated_value,
                "date": dates[i],
                "is_real": False
            })
    
    # Sort by date (oldest first)
    values.sort(key=lambda x: x["date"])
    
    return {
        "test_name": test_name,
        "unit": config["unit"],
        "measurements": values
    }

def calculate_median_by_position_and_age(all_players, current_player, test_name):
    """Calculate median for players with same position and ±3 age range"""
    if not current_player.get('position') or not current_player.get('age'):
        return None
    
    current_position = current_player['position']
    current_age = current_player['age']
    
    # Filter players by position and age range
    similar_players = []
    for player in all_players:
        if (player.get('position') == current_position and 
            player.get('age') and 
            abs(player['age'] - current_age) <= 3):
            similar_players.append(player)
    
    if len(similar_players) < 2:
        return None
    
    # Extract test values (this would need to be implemented based on actual data structure)
    test_values = []
    for player in similar_players:
        # This is a placeholder - you'd need to extract the actual test value
        # from the player's test data
        pass
    
    if test_values:
        return np.median(test_values)
    return None

def calculate_team_median(team_players, test_name):
    """Calculate median for all players in current team"""
    if not team_players:
        return None
    
    # Extract test values (this would need to be implemented based on actual data structure)
    test_values = []
    for player in team_players:
        # This is a placeholder - you'd need to extract the actual test value
        # from the player's test data
        pass
    
    if test_values:
        return np.median(test_values)
    return None

def get_enhanced_athletic_performance(player_id, team_id=None):
    """
    Get enhanced athletic performance data with historical measurements and median comparisons
    """
    try:
        # Get player data
        player = get_player_by_id(player_id)
        if not player:
            return None
        
        # Get team_id from player if not provided
        if not team_id:
            team_id = player.get('teamId')
        
        # Get test instances for the player
        test_instances = get_player_test_instances(player_id)
        
        # Get player thresholds
        player_thresholds = get_player_thresholds(player_id)
        
        # Get team thresholds
        team_thresholds = get_team_thresholds(team_id) if team_id else []
        
        # Extract real test data from test instances
        real_test_data = {}
        print(f"[DEBUG] Processing {len(test_instances) if test_instances else 0} test instances")
        if test_instances:
            for instance in test_instances:
                test_name = instance.get('testName', '')
                date = instance.get('date', '')
                results = instance.get('results', {})
                
                print(f"[DEBUG] Test instance - name: '{test_name}', date: '{date}', results: {results}")
                
                if results and 'rawValue' in results:
                    raw_value = results.get('rawValue')
                    raw_field = results.get('rawField', '')
                    
                    if test_name not in real_test_data:
                        real_test_data[test_name] = []
                    
                    real_test_data[test_name].append({
                        'date': date,
                        'value': raw_value,
                        'field': raw_field
                    })
        
        print(f"[DEBUG] Real test data keys: {list(real_test_data.keys())}")
        
        # Define test categories and their expected test names
        test_categories = {
            'Anthropometry': {
                'Height': {'unit': 'cm', 'std_dev': 2.0, 'is_integer': False},
                'Weight': {'unit': 'kg', 'std_dev': 3.0, 'is_integer': False},
                'BMI': {'unit': '', 'std_dev': 0.5, 'is_integer': False},
                '% BF': {'unit': '%', 'std_dev': 1.0, 'is_integer': False}
            },
            'Power': {
                'Single Leg Jump': {'unit': '%', 'std_dev': 2.0, 'is_integer': False},
                'CMJ Arm Swing HT': {'unit': 'cm', 'std_dev': 3.0, 'is_integer': False},
                'CMJ Arm Locked HT': {'unit': 'cm', 'std_dev': 3.0, 'is_integer': False},
                'Diff % Height Swing-Locked': {'unit': '%', 'std_dev': 1.0, 'is_integer': False}
            },
            'Speed': {
                '5m': {'unit': 's', 'std_dev': 0.1, 'is_integer': False},
                '10m': {'unit': 's', 'std_dev': 0.15, 'is_integer': False},
                '20m': {'unit': 's', 'std_dev': 0.2, 'is_integer': False},
                '30m': {'unit': 's', 'std_dev': 0.25, 'is_integer': False}
            },
            'Agility': {
                'T Test': {'unit': 's', 'std_dev': 0.3, 'is_integer': False},
                'Illinois': {'unit': 's', 'std_dev': 0.4, 'is_integer': False},
                'ArrowHead': {'unit': 's', 'std_dev': 0.4, 'is_integer': False}
            },
            'Endurance': {
                'Lactate': {'unit': 'mmol/L', 'std_dev': 0.5, 'is_integer': False},
                'YYIRT1': {'unit': 'm', 'std_dev': 100, 'is_integer': True},
                'YYIRT2': {'unit': 'm', 'std_dev': 80, 'is_integer': True}
            }
        }
        
        enhanced_data = {}
        
        # Process each test category
        for category, tests in test_categories.items():
            enhanced_data[category] = {}
            
            for test_name, config in tests.items():
                # Look for real data for this test
                real_value = None
                real_date = None
                
                # Try to find matching test data
                for api_test_name, test_results in real_test_data.items():
                    # Check if the API test name contains our test name or vice versa
                    if (test_name.lower() in api_test_name.lower() or 
                        api_test_name.lower() in test_name.lower()):
                        if test_results:
                            # Get the most recent test result
                            latest_result = max(test_results, key=lambda x: x.get('date', ''))
                            real_value = latest_result.get('value')
                            real_date = latest_result.get('date')
                            break
                
                # If no real data found, use player's basic measurements for some tests
                if real_value is None:
                    if test_name == 'Height' and player.get('height'):
                        real_value = player.get('height')
                    elif test_name == 'Weight' and player.get('weight'):
                        real_value = player.get('weight')
                    elif test_name == 'BMI' and player.get('height') and player.get('weight'):
                        height_m = player.get('height') / 100
                        real_value = player.get('weight') / (height_m * height_m)
                    else:
                        # Use reasonable defaults based on test type
                        real_value = get_default_test_value(test_name)
                
                # Generate historical data based on real value
                if real_value is not None:
                    historical_data = generate_historical_data(
                        real_value, 
                        test_name, 
                        num_entries=10,
                        std_dev=config['std_dev'],
                        is_integer=config['is_integer'],
                        unit=config['unit']
                    )
                    
                    enhanced_data[category][test_name] = historical_data
        
        return {
            'player': player,
            'enhanced_data': enhanced_data,
            'test_instances': test_instances,
            'player_thresholds': player_thresholds,
            'team_thresholds': team_thresholds,
            'real_test_data': real_test_data
        }
        
    except Exception as e:
        print(f"Error in get_enhanced_athletic_performance: {e}")
        return None

def get_default_test_value(test_name):
    """
    Get reasonable default values for tests when no real data is available
    """
    defaults = {
        'Height': 175,
        'Weight': 70,
        'BMI': 22.5,
        '% BF': 12,
        'Single Leg Jump': 85,
        'CMJ Arm Swing HT': 45,
        'CMJ Arm Locked HT': 40,
        'Diff % Height Swing-Locked': 7,
        '5m': 1.0,
        '10m': 1.6,
        '20m': 3.0,
        '30m': 3.8,
        'T Test': 10.0,
        'Illinois': 15.0,
        'ArrowHead': 15.3,
        'Lactate': 4.0,
        'YYIRT1': 2400,
        'YYIRT2': 1400
    }
    return defaults.get(test_name, 0)

def generate_historical_data(current_value, test_name, num_entries=10, std_dev=None, is_integer=False, unit=''):
    """
    Generate historical data based on real current value with realistic distribution
    """
    if std_dev is None:
        # Default standard deviation based on test type
        if 'Height' in test_name:
            std_dev = 2.0
        elif 'Weight' in test_name:
            std_dev = 3.0
        elif 'Speed' in test_name or test_name in ['5m', '10m', '20m', '30m']:
            std_dev = 0.15
        elif 'Agility' in test_name or test_name in ['T Test', 'Illinois', 'ArrowHead']:
            std_dev = 0.3
        elif 'Power' in test_name or 'Jump' in test_name:
            std_dev = 3.0
        elif 'Endurance' in test_name or 'YYIRT' in test_name:
            std_dev = 100
        else:
            std_dev = current_value * 0.05  # 5% of current value
    
    # Ensure std_dev is not too small for the data type
    if is_integer and std_dev < 1:
        std_dev = 1
    
    measurements = []
    current_date = datetime.now()
    
    # Generate historical dates (2-4 weeks apart)
    for i in range(num_entries - 1, -1, -1):
        # Calculate date (most recent first)
        weeks_back = (num_entries - 1 - i) * random.uniform(2, 4)
        date = current_date - timedelta(weeks=weeks_back)
        
        if i == 0:  # Most recent measurement (real data)
            value = current_value
            is_real = True
        else:  # Historical measurements (generated)
            # Generate value using normal distribution around current_value
            generated_value = np.random.normal(current_value, std_dev)
            
            # Apply reasonable bounds based on test type
            if 'Height' in test_name:
                generated_value = max(150, min(220, generated_value))
            elif 'Weight' in test_name:
                generated_value = max(50, min(120, generated_value))
            elif 'Speed' in test_name or test_name in ['5m', '10m', '20m', '30m']:
                generated_value = max(0.8, min(5.0, generated_value))
            elif 'Agility' in test_name or test_name in ['T Test', 'Illinois', 'ArrowHead']:
                generated_value = max(8.0, min(20.0, generated_value))
            elif 'Power' in test_name or 'Jump' in test_name:
                generated_value = max(20, min(80, generated_value))
            elif 'Endurance' in test_name or 'YYIRT' in test_name:
                generated_value = max(1000, min(4000, generated_value))
            elif 'BMI' in test_name:
                generated_value = max(16, min(35, generated_value))
            elif '% BF' in test_name:
                generated_value = max(5, min(25, generated_value))
            elif 'Lactate' in test_name:
                generated_value = max(1.0, min(10.0, generated_value))
            
            # Convert to integer if required
            if is_integer:
                generated_value = int(round(generated_value))
            
            value = generated_value
            is_real = False
        
        measurements.append({
            'date': date.strftime('%Y-%m-%d'),
            'value': value,
            'is_real': is_real
        })
    
    return {
        'test_name': test_name,
        'unit': unit,
        'measurements': measurements
    }