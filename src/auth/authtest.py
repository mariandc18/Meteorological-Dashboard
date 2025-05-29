import sys
import os
import pytest
from datetime import datetime

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.auth.authentication_manager import AuthManager
from src.storage.testmodel import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)  # Crear las tablas

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='function')
def auth_manager(db_session):
    return AuthManager(db_session=db_session)


def test_register_user_success(auth_manager):
    user = auth_manager.register_user("testuser", "ValidPass123!")
    assert user.username == "testuser"
    # Aquí verificamos que la contraseña está hasheada (no igual a la original)
    assert user.password_hash != "ValidPass123!"
    assert user.role == "user"


def test_register_user_duplicate(auth_manager):
    auth_manager.register_user("testuser", "ValidPass123!")
    with pytest.raises(ValueError) as e:
        auth_manager.register_user("testuser", "OtherPass123!")
    assert "ya existe" in str(e.value)


def test_register_user_invalid_password(auth_manager):
    with pytest.raises(ValueError) as e:
        auth_manager.register_user("testuser", "short")
    assert "Password error" in str(e.value)


def test_login_user_success(auth_manager):
    auth_manager.register_user("testuser", "ValidPass123!")
    user = auth_manager.login_user("testuser", "ValidPass123!")
    assert user is not None
    assert user.username == "testuser"
    assert user.last_access is not None


def test_login_user_wrong_password(auth_manager):
    auth_manager.register_user("testuser", "ValidPass123!")
    user = auth_manager.login_user("testuser", "WrongPass")
    assert user is None


def test_login_user_not_exist(auth_manager):
    user = auth_manager.login_user("nonexistent", "AnyPass123!")
    assert user is None
