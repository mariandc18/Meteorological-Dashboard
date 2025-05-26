import uuid
import hashlib
import bcrypt

def generate_uid() -> str:
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_user_agent(user_agent: str) -> str:
    return hashlib.sha256(user_agent.encode('utf-8')).hexdigest()
