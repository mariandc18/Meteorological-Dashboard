import uuid
import hashlib
import bcrypt
import re

def generate_uid():
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_user_agent(user_agent: str) -> str:
    return hashlib.sha256(user_agent.encode('utf-8')).hexdigest()

def validate_password(password: str) -> tuple[bool, list[str]]:
    errors = []

    special_chars = set("!@#$%^&*()_+-=[]{}|;:',.<>/?")

    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres.")
    if not any(c.isupper() for c in password):
        errors.append("Debe contener al menos una letra mayúscula.")
    if not any(c.islower() for c in password):
        errors.append("Debe contener al menos una letra minúscula.")
    if not any(c.isdigit() for c in password):
        errors.append("Debe contener al menos un número.")
    if not any(c in special_chars for c in password):
        errors.append("Debe contener al menos un carácter especial.")

    if errors:
        return False, errors
    return True, ["Contraseña válida."]