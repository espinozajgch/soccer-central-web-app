import streamlit as st
from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

DATABASE_URL = f"mysql+mysqlconnector://" + \
    f"{st.secrets.db.username}" + ":" + \
    f"{st.secrets.db.password}" + "@" + \
    f"{st.secrets.db.host}" + ":" + \
    f"{st.secrets.db.port}" + "/" + \
    f"{st.secrets.db.database}"
# e.g. postgresql+psycopg2://user:password@host:port/dbname

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

PEPPER = "soccerCentralHash"
def hash_password(password: str) -> str:
    # passlib returns the hashed password as a string (not bytes)
    return passlib_bcrypt.hash(password + PEPPER)

def check_password(password: str, hashed: str) -> bool:
    # passlib automatically handles salt & algorithm from the stored hash
    return passlib_bcrypt.verify(password + PEPPER, hashed)

def get_all_players(conn):
    query = """
    SELECT p.player_id, u.first_name, u.last_name, p.number, p.primary_position
    FROM players p
    JOIN users u ON p.user_id = u.user_id
    ORDER BY u.last_name, u.first_name
    """
    return pd.read_sql_query(query, conn)

def get_player_details(conn, player_id):
    query = """
    SELECT 
        p.player_id,
        u.first_name,
        u.last_name,
        u.birth_date,
        u.gender,
        u.email,
        u.phone,
        u.country,
        u.photo_url,
        p.number,
        p.school_name,
        p.primary_position,
        p.secondary_position,
        p.grade_level,
        p.shirt_size,
        p.short_size,
        p.country_of_birth,
        p.country_of_citizenship,
        p.nationality,
        p.city,
        p.training_location,
        p.registration_date,
        p.education_level,
        p.last_team,
        p.dominant_foot,
        p.height,
        p.athlete_number,
        p.graduation_date,
        p.insurance_company,
        p.insurance_policy_number,
        p.health_notes,
        p.player_activity_history,
        p.notes
    FROM players p
    JOIN users u ON p.user_id = u.user_id
    WHERE p.player_id = %(player_id)s
    """
    df = pd.read_sql_query(query, conn, params={"player_id": player_id})
    return df.iloc[0].to_dict() if not df.empty else {}

def get_player_teams(conn, player_id):
    query = """
    SELECT 
        pt.id,
        pt.player_id,
        pt.team_id,
        t.name as team_name,
        pt.start_date,
        pt.end_date,
        t.notes
    FROM player_teams pt
    JOIN teams t ON pt.team_id = t.team_id
    WHERE pt.player_id = %(player_id)s
    ORDER BY pt.start_date
    """
    return pd.read_sql_query(query, conn, params={"player_id": player_id})

def get_player_games(conn, player_id):
    query = """
    SELECT 
        pgs.id,
        pgs.game_id,
        g.match_date,
        t_home.name as home_team,
        t_away.name as away_team,
        g.final_score,
        pgs.starter,
        pgs.goals,
        pgs.minutes_played
    FROM player_game_stats pgs
    JOIN games g ON pgs.game_id = g.game_id
    JOIN teams t_home ON g.team_home_id = t_home.team_id
    JOIN teams t_away ON g.team_away_id = t_away.team_id
    WHERE pgs.player_id = %(player_id)s
    ORDER BY g.match_date
    """
    df = pd.read_sql_query(query, conn, params={"player_id": player_id})
    if not df.empty and 'starter' in df.columns:
        df['starter'] = df['starter'].astype(bool)
    return df

def get_player_metrics(conn, player_id):
    query = """
    SELECT * 
    FROM metrics
    WHERE player_id = %(player_id)s
    ORDER BY training_date
    """
    return pd.read_sql_query(query, conn, params={"player_id": player_id})

def get_player_evaluations(conn, player_id):
    query = """
    SELECT * 
    FROM player_evaluations
    WHERE player_id = %(player_id)s
    ORDER BY evaluation_date DESC
    """
    return pd.read_sql_query(query, conn, params={"player_id": player_id})

def get_player_videos(conn, player_id):
    query = """
    SELECT 
        pv.id,
        pv.player_id,
        pv.video_id,
        v.url,
        pv.description,
        g.match_date
    FROM player_videos pv
    JOIN videos v ON pv.video_id = v.video_id
    LEFT JOIN games g ON v.game_id = g.game_id
    WHERE pv.player_id = %(player_id)s
    ORDER BY g.match_date DESC
    """
    return pd.read_sql_query(query, conn, params={"player_id": player_id})

def get_player_documents(conn, player_id):
    query = """
    SELECT * 
    FROM player_documents
    WHERE player_id = %(player_id)s
    ORDER BY uploaded_at DESC
    """
    return pd.read_sql_query(query, conn, params={"player_id": player_id})

def get_team_players(conn, team_id):
    query = """
    SELECT 
        p.player_id,
        u.first_name,
        u.last_name,
        p.number,
        p.primary_position,
        p.secondary_position
    FROM players p
    JOIN users u ON p.user_id = u.user_id
    JOIN player_teams pt ON p.player_id = pt.player_id
    WHERE pt.team_id = %(team_id)s
    ORDER BY u.last_name, u.first_name
    """
    return pd.read_sql_query(query, conn, params={"team_id": team_id})

def get_position_distribution(conn, team_id):
    query = """
    SELECT 
        p.primary_position,
        COUNT(*) as count
    FROM players p
    JOIN player_teams pt ON p.player_id = pt.player_id
    WHERE pt.team_id = %(team_id)s
    GROUP BY p.primary_position
    """
    return pd.read_sql_query(query, conn, params={"team_id": team_id})