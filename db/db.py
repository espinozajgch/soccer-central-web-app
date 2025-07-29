from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os
from dotenv import load_dotenv


# Cargar .env desde el directorio raíz del proyecto
load_dotenv()

# Leer variables de entorno
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Opcional: si quieres usar hashing con pepper
PEPPER = "soccerCentralHash"

def hash_password(password: str) -> str:
    return passlib_bcrypt.hash(password + PEPPER)

def check_password(password: str, hashed: str) -> bool:
    return passlib_bcrypt.verify(password + PEPPER, hashed)

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
