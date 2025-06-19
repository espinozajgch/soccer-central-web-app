from db.db import SessionLocal
from db.models import Users

def get_user(username):
    session = SessionLocal()
    try:
        user = session.query(Users).filter_by(email=username).first()
        return user if user else None
    finally:
        session.close()