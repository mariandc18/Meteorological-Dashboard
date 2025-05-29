from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, Any, Optional, List
from sqlalchemy import text

class PostgreSQLDBManager:
    def __init__(self, model: Type[Any]):
        """
        model: Clase del modelo SQLAlchemy (por ejemplo, User, Product, etc.)
        """
        self.model = model

    def create_record(self, db: Session, data: dict) -> Optional[Any]:
        try:
            instance = self.model(**data)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al crear registro: {e}")
            return None

    def read_record(self, db: Session, record_id: Any) -> Optional[Any]:
        try:
            return db.query(self.model).get(record_id)
        except SQLAlchemyError as e:
            print(f"Error al leer registro: {e}")
            return None

    def update_record(self, db: Session, record_id: Any, update_data: dict) -> bool:
        try:
            instance = db.query(self.model).get(record_id)
            if not instance:
                return False
            for key, value in update_data.items():
                setattr(instance, key, value)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al actualizar registro: {e}")
            return False

    def delete_record(self, db: Session, record_id: Any) -> bool:
        try:
            instance = db.query(self.model).get(record_id)
            if not instance:
                return False
            db.delete(instance)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al eliminar registro: {e}")
            return False

    def insert_many(self, db: Session, records: List[dict]) -> List[Any]:
        try:
            instances = [self.model(**record) for record in records]
            db.bulk_save_objects(instances)
            db.commit()
            return instances
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al insertar múltiples registros: {e}")
            return []

    def list_all(self, db: Session) -> List[Any]:
        try:
            return db.query(self.model).all()
        except SQLAlchemyError as e:
            print(f"Error al listar registros: {e}")
            return []

    def drop_table(self, db: Session):
        try:
            self.model.__table__.drop(db.bind)
            print(f"Tabla '{self.model.__tablename__}' eliminada.")
        except SQLAlchemyError as e:
            print(f"Error al eliminar tabla: {e}")
    
    def drop_column(self, db: Session, column_name: str) -> bool:
        try:
            table_name = self.model.__tablename__
            stmt = text(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}')
            db.execute(stmt)
            db.commit()
            print(f"Columna '{column_name}' eliminada de la tabla '{table_name}'.")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al eliminar columna '{column_name}': {e}")
            return False