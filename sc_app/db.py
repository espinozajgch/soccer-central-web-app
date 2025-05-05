import bcrypt
PEPPER = "soccerCentralHash"

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw((password + PEPPER).encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw((password + PEPPER).encode('utf-8'), hashed)