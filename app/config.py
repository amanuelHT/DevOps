import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fdsafasd")
    UPLOAD_FOLDER = "image_pool"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return ProdConfig if env == "production" else DevConfig
