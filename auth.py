from db import SessionLocal
from models import Users

def get_user(username):
    session = SessionLocal()
    try:
        user = session.query(Users).filter_by(email=username).first()
        return user.password_hash if user else None
    finally:
        session.close()