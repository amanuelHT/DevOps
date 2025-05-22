import pytest
import sys
import os

# Add current directory to the import path so Python can find app.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import app as flask_app
from database import add_user, delete_user_from_db

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def test_user():
    user_id = "TESTUSER"
    password = "test123"
    delete_user_from_db(user_id)  # Clean slate
    add_user(user_id, password)
    yield user_id, password
    delete_user_from_db(user_id)  # Cleanup

@pytest.fixture(scope="function")
def admin_user():
    user_id = "ADMIN"
    password = "admin"
    delete_user_from_db(user_id)
    add_user(user_id, password)
    yield user_id, password
    delete_user_from_db(user_id)
