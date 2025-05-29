import os

from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DB_USER", os.environ.get("DB_USER"))
DB_PASS = os.getenv("DB_PASS", os.environ.get("DB_PASS"))
DB_HOST = os.getenv("DB_HOST", os.environ.get("DB_HOST"))
DB_PORT = os.getenv("DB_PORT", os.environ.get("DB_PORT"))
DB_NAME = os.getenv("DB_NAME", os.environ.get("DB_NAME"))

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&connect_timeout=10"
