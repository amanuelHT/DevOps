import os

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "defaultsecret")
    UPLOAD_FOLDER = "image_pool"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

config = BaseConfig()  # ✅ Now you can do `from config import config`
