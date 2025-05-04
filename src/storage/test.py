import pytest
from bson import ObjectId
from bson.errors import InvalidId
from db_manager import MongoDBManager

@pytest.fixture(scope="function")
def db():
    test_db = "test_db"
    test_collection = "test_collection"
    
    db_manager = MongoDBManager(test_db, test_collection)
    db_manager.collection.delete_many({})  # Limpieza inicial
    
    yield db_manager
    
    # Limpieza después de cada test (antes de cerrar la conexión)
    if db_manager.client:
        try:
            db_manager.collection.delete_many({})
        except:
            pass
        db_manager.close_connection()

def test_connection(db):
    assert db.client is not None
    assert db.db.name == "test_db"
    assert db.collection.name == "test_collection"

def test_create_document(db):
    # Test creación válida
    valid_data = {"name": "Test", "value": 123}
    doc_id = db.create_document(valid_data)
    assert ObjectId.is_valid(doc_id)
    
    # Test creación inválida (intento de inyección de operador)
    invalid_data = {"$set": {"name": "Hack"}}
    invalid_id = db.create_document(invalid_data)
    assert invalid_id is None  # Debería fallar y retornar None

def test_read_document(db):
    # Crear documento de prueba
    doc_id = db.create_document({"name": "Read Test"})
    
    # Caso exitoso
    doc = db.read_document(doc_id)
    assert doc["name"] == "Read Test"
    
    # Caso con ID inválido
    assert db.read_document("invalid_id") is None
    
    # Caso con ID inexistente
    fake_id = str(ObjectId())
    assert db.read_document(fake_id) is None

def test_update_document(db):
    # Crear documento de prueba
    doc_id = db.create_document({"name": "Original"})
    
    # Caso exitoso
    update_result = db.update_document(doc_id, {"name": "Updated"})
    assert update_result is True
    
    # Verificar actualización
    updated_doc = db.read_document(doc_id)
    assert updated_doc["name"] == "Updated"
    
    # Caso con ID inválido
    assert db.update_document("invalid_id", {"name": "Fail"}) is False

def test_delete_document(db):
    # Crear documento de prueba
    doc_id = db.create_document({"name": "To Delete"})
    
    # Caso exitoso
    delete_result = db.delete_document(doc_id)
    assert delete_result is True
    
    # Verificar eliminación
    assert db.read_document(doc_id) is None
    
    # Caso con ID inválido
    assert db.delete_document("invalid_id") is False

def test_list_databases(db):
    databases = db.list_databases()
    assert isinstance(databases, list)
    assert "test_db" in databases

def test_list_collections(db):
    collections = db.list_collections()
    assert isinstance(collections, list)
    assert "test_collection" in collections

def test_set_collection(db):
    new_collection = "new_test_collection"
    db.set_collection(new_collection)
    assert db.collection.name == new_collection
    
    # Restaurar colección original
    db.set_collection("test_collection")

def test_drop_collection(db):
    temp_collection = "temp_collection"
    db.set_collection(temp_collection)
    
    # Insertar documento y eliminar colección
    db.create_document({"test": "data"})
    db.drop_collection()
    
    # Verificar eliminación
    assert temp_collection not in db.list_collections()
    
    # Restaurar configuración original
    db.set_collection("test_collection")

def test_close_connection(db):
    # Cerrar conexión
    db.close_connection()
    
    # Verificar que el cliente está marcado como cerrado
    assert db.client is None
    
    # Verificar que nuevas operaciones fallan
    with pytest.raises(AttributeError):
        db.create_document({"test": "data"})