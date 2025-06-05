import streamlit as st
from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import func, create_engine
from sqlalchemy.orm import aliased, sessionmaker
from models import (
    Players, Users, PlayerTeams, Teams, PlayerGameStats, Games, Metrics,
    PlayerEvaluations, PlayerVideos, Videos, PlayerDocuments
)

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

# @todo Use following functions

def get_all_players(session):
    return (
        session.query(
            Players.player_id,
            Users.first_name,
            Users.last_name,
            Players.number,
            Players.primary_position
        )
        .join(Users, Players.user_id == Users.user_id)
        .order_by(Users.last_name, Users.first_name)
        .all()
    )

def get_player_details(session, player_id):
    result = (
        session.query(
            Players.player_id,
            Users.first_name,
            Users.last_name,
            Users.birth_date,
            Users.gender,
            Users.email,
            Users.phone,
            Users.country,
            Users.photo_url,
            Players.number,
            Players.school_name,
            Players.primary_position,
            Players.secondary_position,
            Players.grade_level,
            Players.shirt_size,
            Players.short_size,
            Players.country_of_birth,
            Players.country_of_citizenship,
            Players.nationality,
            Players.city,
            Players.training_location,
            Players.registration_date,
            Players.education_level,
            Players.last_team,
            Players.dominant_foot,
            Players.height,
            Players.athlete_number,
            Players.graduation_date,
            Players.insurance_company,
            Players.insurance_policy_number,
            Players.health_notes,
            Players.player_activity_history,
            Players.notes
        )
        .join(Users, Players.user_id == Users.user_id)
        .filter(Players.player_id == player_id)
        .first()
    )
    return result._asdict() if result else {}

def get_player_teams(session, player_id):
    return (
        session.query(
            PlayerTeams.id,
            PlayerTeams.player_id,
            PlayerTeams.team_id,
            Teams.name.label('team_name'),
            PlayerTeams.start_date,
            PlayerTeams.end_date,
            Teams.notes
        )
        .join(Teams, PlayerTeams.team_id == Teams.team_id)
        .filter(PlayerTeams.player_id == player_id)
        .order_by(PlayerTeams.start_date)
        .all()
    )

def get_player_games(session, player_id):
    Teams_2 = aliased(Teams)
    return (
        session.query(
            PlayerGameStats.id,
            PlayerGameStats.game_id,
            Games.match_date,
            Teams.name.label('home_team'),
            Teams_2.name.label('away_team'),
            Games.final_score,
            PlayerGameStats.starter,
            PlayerGameStats.goals,
            PlayerGameStats.minutes_played
        )
        .join(Games, PlayerGameStats.game_id == Games.game_id)
        .join(Teams, Games.team_home_id == Teams.team_id)
        .join(Teams_2, Games.team_away_id == Teams_2.team_id)
        .filter(PlayerGameStats.player_id == player_id)
        .order_by(Games.match_date)
        .all()
    )

def get_player_metrics(session, player_id):
    return (
        session.query(Metrics)
        .filter(Metrics.player_id == player_id)
        .order_by(Metrics.training_date)
        .all()
    )

def get_player_evaluations(session, player_id):
    return (
        session.query(PlayerEvaluations)
        .filter(PlayerEvaluations.player_id == player_id)
        .order_by(PlayerEvaluations.evaluation_date.desc())
        .all()
    )

def get_player_videos(session, player_id):
    return (
        session.query(
            PlayerVideos.id,
            PlayerVideos.player_id,
            PlayerVideos.video_id,
            Videos.url,
            PlayerVideos.description,
            Games.match_date
        )
        .join(Videos, PlayerVideos.video_id == Videos.video_id)
        .outerjoin(Games, Videos.game_id == Games.game_id)
        .filter(PlayerVideos.player_id == player_id)
        .order_by(Games.match_date.desc())
        .all()
    )

def get_player_documents(session, player_id):
    return (
        session.query(PlayerDocuments)
        .filter(PlayerDocuments.player_id == player_id)
        .order_by(PlayerDocuments.uploaded_at.desc())
        .all()
    )

def get_team_players(session, team_id):
    return (
        session.query(
            Players.player_id,
            Users.first_name,
            Users.last_name,
            Players.number,
            Players.primary_position,
            Players.secondary_position
        )
        .join(Users, Players.user_id == Users.user_id)
        .join(PlayerTeams, Players.player_id == PlayerTeams.player_id)
        .filter(PlayerTeams.team_id == team_id)
        .order_by(Users.last_name, Users.first_name)
        .all()
    )

def get_position_distribution(session, team_id):
    return (
        session.query(
            Players.primary_position,
            func.count().label('count')
        )
        .join(PlayerTeams, Players.player_id == PlayerTeams.player_id)
        .filter(PlayerTeams.team_id == team_id)
        .group_by(Players.primary_position)
        .all()
    )
