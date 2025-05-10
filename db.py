import os

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

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
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw((password + PEPPER).encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw((password + PEPPER).encode('utf-8'), hashed)