from src.auth.security import hash_password, verify_password, generate_uid, validate_password
from src.storage.tables import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from src.storage.config import DATABASE_URL

class AuthManager:
    def __init__(self, db_session: Session = None):
        if db_session is None:
            self.engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
            Base.metadata.create_all(self.engine)
            SessionLocal = sessionmaker(bind=self.engine)
            self.db = SessionLocal()
        else:
            self.db = db_session

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
            cookie_uid=generate_uid(),  # debe devolver string UUID
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

    def close(self):
        self.db.close()
