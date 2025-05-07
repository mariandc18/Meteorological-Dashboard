import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from bson import ObjectId
from bson.errors import InvalidId  # Nuevo import

class MongoDBManager:
    def __init__(self, db_name=None, collection_name=None):        
        self.uri = "mongodb+srv://reinaldo:rcg06a00@cluster0.e0x1rrc.mongodb.net/"
        self.client = None
        self.db = None
        self.collection = None
        
        try:
            self.client = MongoClient(
                self.uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                retryWrites=True,
                socketTimeoutMS=30000,
                connectTimeoutMS=30000
            )
            self.client.admin.command('ping')
            print("Conectado a MongoDB Atlas")
            
            if db_name:
                self.db = self.client[db_name]
                if collection_name:
                    self.collection = self.db[collection_name]
                    
        except ConnectionFailure as e:
            print(f"Error de conexión: {e}")
            raise

    def set_collection(self, collection_name):
        if self.db is not None:  # Corregido
            self.collection = self.db[collection_name]

    def create_document(self, data):
        try:
            # Validar datos básicos
            if not isinstance(data, dict) or not data:
                raise ValueError("Datos inválidos")

            # Prevenir inyección de operadores
            if any(key.startswith('$') for key in data):
                raise ValueError("Operadores prohibidos")

            result = self.collection.insert_one(data.copy())  # Usar copia para seguridad
            return str(result.inserted_id)

        except (PyMongoError, ValueError) as e:
            print(f"Error al crear documento: {e}")
            return None

    def read_document(self, document_id):
        try:
            ObjectId(document_id)  # Validación explícita
            doc = self.collection.find_one({"_id": ObjectId(document_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except (PyMongoError, InvalidId) as e:  # Captura múltiple
            print(f"Error al leer documento: {e}")
            return None
        
    def insert_many(self, documents):
        try:
            if not isinstance(documents, list) or not all(isinstance(doc, dict) for doc in documents):
                raise ValueError("Debe ser una lista de diccionarios")
            for doc in documents:
                if any(key.startswith('$') for key in doc):
                    raise ValueError("Operadores prohibidos en alguno de los documentos")

            result = self.collection.insert_many(documents)  # Insertar múltiples documentos
            return [str(inserted_id) for inserted_id in result.inserted_ids]  # Devolver IDs insertados como cadenas
        except (PyMongoError, ValueError) as e:
            print(f"Error al insertar múltiples documentos: {e}")
            return None
        

    def update_document(self, document_id, update_data):
        try:
            ObjectId(document_id)  # Validación explícita
            result = self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except (PyMongoError, InvalidId) as e:  # Captura múltiple
            print(f"Error al actualizar documento: {e}")
            return False

    def delete_document(self, document_id):
        try:
            ObjectId(document_id)  # Validación explícita
            result = self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except (PyMongoError, InvalidId) as e:  # Captura múltiple
            print(f"Error al eliminar documento: {e}")
            return False

    def list_databases(self):
        return self.client.list_database_names()

    def list_collections(self):
        return self.db.list_collection_names()

    def drop_collection(self):
        if self.collection is not None:
            self.db.drop_collection(self.collection.name)

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None  # Marcar explícitamente como cerrado
            self.db = None
            self.collection = None
            print("Conexión cerrada")
        