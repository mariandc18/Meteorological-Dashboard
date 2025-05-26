from auth.security import hash_password, verify_password, generate_uid, hash_user_agent
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

    def register_guest(self, ip_address: str, user_agent: str):
        guest = User(
            role='guest',
            cookie_uid=generate_uid(),
            ip_address=ip_address,
            user_agent=user_agent,
            analysis_count=0,
            created_at=datetime.utcnow()
        )
        self.db.add(guest)
        self.db.commit()
        self.db.refresh(guest)
        return guest

    def upgrade_guest_to_user(self, guest_uid: str, username: str, password: str, email: str = None):
        guest = self.db.query(User).filter(User.cookie_uid == guest_uid, User.role == 'guest').first()
        if not guest:
            return None
        guest.username = username
        guest.email = email
        guest.password = hash_password(password)
        guest.role = 'user'
        guest.last_access = datetime.utcnow()
        self.db.commit()
        self.db.refresh(guest)
        return guest