from src.storage.db_manager import MongoDBManager

# Conexión única a MongoDB, accesible desde toda la aplicación
locations_collection = MongoDBManager(db_name="weather_db", collection_name="locations")
weather_hourly_collection = MongoDBManager(db_name="weather_db", collection_name="weather_hourly")
weather_daily_collection = MongoDBManager(db_name="weather_db", collection_name="weather_daily")