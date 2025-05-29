import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testmodel import Base, TestModel
from db_manager import PostgreSQLDBManager 


TEST_DATABASE_URL = "sqlite:///:memory:"  
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)  # Crear tablas antes de cada test
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)  # Limpiar tablas después de cada test

@pytest.fixture(scope="function")
def db_manager():
    return PostgreSQLDBManager(TestModel)

def test_create_record(db_session, db_manager):
    data = {"name": "Test", "value": 123}
    record = db_manager.create_record(db_session, data)
    assert record is not None
    assert record.id is not None
    assert record.name == "Test"
    assert record.value == 123

def test_read_record(db_session, db_manager):
    data = {"name": "ReadTest", "value": 10}
    record = db_manager.create_record(db_session, data)
    read = db_manager.read_record(db_session, record.id)
    assert read is not None
    assert read.name == "ReadTest"

    # Leer registro que no existe
    assert db_manager.read_record(db_session, 9999) is None

def test_update_record(db_session, db_manager):
    data = {"name": "Original", "value": 1}
    record = db_manager.create_record(db_session, data)
    updated = db_manager.update_record(db_session, record.id, {"name": "Updated"})
    assert updated is True

    updated_record = db_manager.read_record(db_session, record.id)
    assert updated_record.name == "Updated"

    # Actualizar registro no existente
    assert db_manager.update_record(db_session, 9999, {"name": "Fail"}) is False

def test_delete_record(db_session, db_manager):
    data = {"name": "ToDelete", "value": 5}
    record = db_manager.create_record(db_session, data)
    deleted = db_manager.delete_record(db_session, record.id)
    assert deleted is True

    assert db_manager.read_record(db_session, record.id) is None

    # Eliminar registro no existente
    assert db_manager.delete_record(db_session, 9999) is False

def test_insert_many(db_session, db_manager):
    records = [
        {"name": "Bulk1", "value": 1},
        {"name": "Bulk2", "value": 2},
    ]
    inserted = db_manager.insert_many(db_session, records)
    assert len(inserted) == 2
    names = [r.name for r in inserted]
    assert "Bulk1" in names and "Bulk2" in names

def test_list_all(db_session, db_manager):
    db_manager.create_record(db_session, {"name": "List1", "value": 100})
    db_manager.create_record(db_session, {"name": "List2", "value": 200})
    all_records = db_manager.list_all(db_session)
    assert len(all_records) >= 2

def test_drop_column(db_session, db_manager):
    # Insertar un registro para asegurar la tabla está activa
    db_manager.create_record(db_session, {"name": "TestDrop", "value": 1})
    
    # Drop columna "value"
    success = db_manager.drop_column(db_session, "value")
    assert success is True

    # Intentar dropear una columna que no existe
    success = db_manager.drop_column(db_session, "nonexistent_column")
    assert success is True  # El DROP COLUMN IF EXISTS no falla si no existe

def test_drop_table(db_session, db_manager):
    # Drop tabla entera
    db_manager.drop_table(db_session)

    # Verificar que la tabla no existe consultando metadata
    assert not engine.dialect.has_table(engine.connect(), db_manager.model.__tablename__)
