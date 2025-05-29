from auth.security import hash_password, verify_password, generate_uid, hash_user_agent, validate_password
from tables import User
from pages.db import get_db_session
from sqlalchemy.orm import Session
from datetime import datetime

class AuthManager:
    def __init__(self):
        self.db: Session = get_db_session()

    def register_user(self, username: str, password: str, email: str = None):
        if self.db.query(User).filter(User.username == username).first():
            raise ValueError("El usuario ya existe")
        
        is_valid, error_messages = validate_password(password)
        if not is_valid:
            raise ValueError("Password error: " + " | ".join(error_messages))

        
        hashed_pw = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_pw, 
            role='user',
            cookie_uid=generate_uid(),
            created_at=datetime.utcnow()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def login_user(self, username: str, password: str):
        user = self.db.query(User).filter(User.username == username).first()
        if user and user.password and verify_password(password, user.password):
            user.last_access = datetime.utcnow()
            self.db.commit()
            return user
        return None