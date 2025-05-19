import os

# Default SQLite URL for development/tests
DEFAULT_SQLITE_URL = "sqlite:///database_file/flask.db"

# Pull in Postgres credentials if set
PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB   = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres-staging")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

if PG_USER and PG_PASS and PG_DB:
    # In staging/production, build a full Postgres URL
    DATABASE_URL = (
        f"postgresql://{PG_USER}:{PG_PASS}@"
        f"{PG_HOST}:{PG_PORT}/{PG_DB}"
    )
else:
    # Otherwise (dev or missing vars), use SQLite
    DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

SECRET_KEY         = os.getenv("SECRET_KEY", "fdsafasd")
UPLOAD_FOLDER      = os.getenv("UPLOAD_FOLDER", "image_pool")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
