import os

# Detect Postgres vs SQLite automatically
PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB   = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres-staging")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

if PG_USER and PG_PASS and PG_DB:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )
else:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///database_file/flask.db"
    )

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY                = os.getenv("SECRET_KEY", "fdsafasd")
UPLOAD_FOLDER             = os.getenv("UPLOAD_FOLDER", "image_pool")
MAX_CONTENT_LENGTH        = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
