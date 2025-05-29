import uuid
import hashlib
import bcrypt
import re

def generate_uid() -> str:
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_user_agent(user_agent: str) -> str:
    return hashlib.sha256(user_agent.encode('utf-8')).hexdigest()

def validar_contraseña(password: str) -> tuple[bool, list[str]]:
    errores = []

    especiales = set("!@#$%^&*()_+-=[]{}|;:',.<>/?")

    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres.")
    if not any(c.isupper() for c in password):
        errores.append("Debe contener al menos una letra mayúscula.")
    if not any(c.islower() for c in password):
        errores.append("Debe contener al menos una letra minúscula.")
    if not any(c.isdigit() for c in password):
        errores.append("Debe contener al menos un número.")
    if not any(c in especiales for c in password):
        errores.append("Debe contener al menos un carácter especial.")

    if errores:
        return False, errores
    return True, ["Contraseña válida."]