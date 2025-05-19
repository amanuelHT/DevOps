import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database_file/flask.db")



SECRET_KEY = "fdsafasd"
UPLOAD_FOLDER = "image_pool"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024