import streamlit as st
from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import func, create_engine
from sqlalchemy.orm import aliased, sessionmaker, joinedload
from db.models import (
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
