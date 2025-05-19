import os

# Database URL: defaults to SQLite for development; override with a Postgres URL in staging/production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///database_file/flask.db"
)

# Flask secret key (override in production via env var)
SECRET_KEY = os.getenv("SECRET_KEY", "fdsafasd")

# File uploads
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "image_pool")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
