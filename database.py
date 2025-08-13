import sqlite3
import json
from datetime import datetime, timedelta
import os

class MedianCache:
    def __init__(self, db_path="median_cache.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create team median cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_median_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                team_id TEXT NOT NULL,
                median_value REAL NOT NULL,
                player_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(test_name, team_id)
            )
        ''')
        
        # Create position-age median cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_age_median_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                position TEXT NOT NULL,
                age_range TEXT NOT NULL,  -- e.g., "22-25", "26-29"
                median_value REAL NOT NULL,
                player_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(test_name, position, age_range)
            )
        ''')
        
        # Create cache invalidation log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_invalidation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invalidated_by TEXT NOT NULL,
                invalidated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        ''')
        
        # Create test instances cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_instances_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                test_instances_data TEXT NOT NULL,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(player_id)
            )
        ''')
        
        # Create test data cache table (for batch player test data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_data_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT NOT NULL,  -- e.g., "all_players" or "team_123"
                test_data TEXT NOT NULL,  -- JSON string
                player_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(cache_key)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_cached_team_median(self, test_name, team_id):
        """Get cached team median value if it exists and is not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT median_value, expires_at 
            FROM team_median_cache 
            WHERE test_name = ? AND team_id = ?
        ''', (test_name, team_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            median_value, expires_at = result
            expires_at = datetime.fromisoformat(expires_at)
            
            # Check if cache is still valid (7 days expiration)
            if expires_at > datetime.now():
                return median_value
        
        return None
    
    def get_cached_position_age_median(self, test_name, position, age_range):
        """Get cached position-age median value if it exists and is not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT median_value, expires_at 
            FROM position_age_median_cache 
            WHERE test_name = ? AND position = ? AND age_range = ?
        ''', (test_name, position, age_range))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            median_value, expires_at = result
            expires_at = datetime.fromisoformat(expires_at)
            
            # Check if cache is still valid (7 days expiration)
            if expires_at > datetime.now():
                return median_value
        
        return None
    
    def cache_team_median(self, test_name, team_id, median_value, player_count):
        """Cache team median value with 7-day expiration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute('''
            INSERT OR REPLACE INTO team_median_cache 
            (test_name, team_id, median_value, player_count, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_name, team_id, median_value, player_count, expires_at))
        
        conn.commit()
        conn.close()
    
    def cache_position_age_median(self, test_name, position, age_range, median_value, player_count):
        """Cache position-age median value with 7-day expiration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute('''
            INSERT OR REPLACE INTO position_age_median_cache 
            (test_name, position, age_range, median_value, player_count, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (test_name, position, age_range, median_value, player_count, expires_at))
        
        conn.commit()
        conn.close()
    
    def invalidate_all_cache(self, invalidated_by, reason="Manual invalidation"):
        """Invalidate all cached data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear all cache
        cursor.execute('DELETE FROM team_median_cache')
        cursor.execute('DELETE FROM position_age_median_cache')
        cursor.execute('DELETE FROM test_instances_cache')
        cursor.execute('DELETE FROM test_data_cache')
        
        # Log the invalidation
        cursor.execute('''
            INSERT INTO cache_invalidation_log (invalidated_by, reason)
            VALUES (?, ?)
        ''', (invalidated_by, reason))
        
        conn.commit()
        conn.close()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Team median cache stats
        cursor.execute('SELECT COUNT(*) FROM team_median_cache')
        team_total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM team_median_cache WHERE expires_at < ?', (datetime.now(),))
        team_expired_entries = cursor.fetchone()[0]
        
        # Position-age median cache stats
        cursor.execute('SELECT COUNT(*) FROM position_age_median_cache')
        pos_age_total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM position_age_median_cache WHERE expires_at < ?', (datetime.now(),))
        pos_age_expired_entries = cursor.fetchone()[0]
        
        # Test instances cache stats
        cursor.execute('SELECT COUNT(*) FROM test_instances_cache')
        test_instances_total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM test_instances_cache WHERE expires_at < ?', (datetime.now(),))
        test_instances_expired_entries = cursor.fetchone()[0]
        
        # Test data cache stats
        cursor.execute('SELECT COUNT(*) FROM test_data_cache')
        test_data_total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM test_data_cache WHERE expires_at < ?', (datetime.now(),))
        test_data_expired_entries = cursor.fetchone()[0]
        
        # Combined stats
        total_entries = team_total_entries + pos_age_total_entries + test_instances_total_entries + test_data_total_entries
        expired_entries = team_expired_entries + pos_age_expired_entries + test_instances_expired_entries + test_data_expired_entries
        valid_entries = total_entries - expired_entries
        
        # Last invalidation
        cursor.execute('''
            SELECT invalidated_by, invalidated_at, reason 
            FROM cache_invalidation_log 
            ORDER BY invalidated_at DESC 
            LIMIT 1
        ''')
        last_invalidation = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'team_entries': team_total_entries,
            'position_age_entries': pos_age_total_entries,
            'test_instances_entries': test_instances_total_entries,
            'test_data_entries': test_data_total_entries,
            'last_invalidation': last_invalidation
        }
    
    def cleanup_expired_cache(self):
        """Remove expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM team_median_cache WHERE expires_at < ?', (datetime.now(),))
        team_deleted_count = cursor.rowcount
        
        cursor.execute('DELETE FROM position_age_median_cache WHERE expires_at < ?', (datetime.now(),))
        pos_age_deleted_count = cursor.rowcount
        
        cursor.execute('DELETE FROM test_instances_cache WHERE expires_at < ?', (datetime.now(),))
        test_instances_deleted_count = cursor.rowcount
        
        cursor.execute('DELETE FROM test_data_cache WHERE expires_at < ?', (datetime.now(),))
        test_data_deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return team_deleted_count + pos_age_deleted_count + test_instances_deleted_count + test_data_deleted_count
    
    def get_cached_test_instances(self, player_id):
        """Get cached test instances for a player if they exist and are not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT test_instances_data, expires_at 
            FROM test_instances_cache 
            WHERE player_id = ?
        ''', (player_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            test_instances_data, expires_at = result
            expires_at = datetime.fromisoformat(expires_at)
            
            # Check if cache is still valid (1 day expiration for test instances)
            if expires_at > datetime.now():
                return json.loads(test_instances_data)
        
        return None
    
    def cache_test_instances(self, player_id, test_instances_data):
        """Cache test instances for a player with 1-day expiration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(days=1)
        
        cursor.execute('''
            INSERT OR REPLACE INTO test_instances_cache 
            (player_id, test_instances_data, expires_at)
            VALUES (?, ?, ?)
        ''', (player_id, json.dumps(test_instances_data), expires_at))
        
        conn.commit()
        conn.close()
    
    def get_cached_test_data(self, cache_key):
        """Get cached test data for a batch of players if it exists and is not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT test_data, expires_at 
            FROM test_data_cache 
            WHERE cache_key = ?
        ''', (cache_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            test_data, expires_at = result
            expires_at = datetime.fromisoformat(expires_at)
            
            # Check if cache is still valid (1 day expiration for test data)
            if expires_at > datetime.now():
                return json.loads(test_data)
        
        return None
    
    def cache_test_data(self, cache_key, test_data, player_count):
        """Cache test data for a batch of players with 1-day expiration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(days=1)
        
        cursor.execute('''
            INSERT OR REPLACE INTO test_data_cache 
            (cache_key, test_data, player_count, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (cache_key, json.dumps(test_data), player_count, expires_at))
        
        conn.commit()
        conn.close()
    
    def get_age_range(self, age):
        """Generate age range string for caching (e.g., 22 -> '22-25')"""
        if age is None:
            return "25-28"  # Default range
        
        # Handle ages less than 18
        if age < 18:
            if age < 14:
                return "14-17"  # Young players
            elif age < 16:
                return "14-17"  # U16 range
            else:
                return "16-19"  # U18 range
        
        # Create 4-year ranges for adults: 18-21, 22-25, 26-29, 30-33, etc.
        start_age = (age // 4) * 4 + 18
        end_age = start_age + 3
        return f"{start_age}-{end_age}"
