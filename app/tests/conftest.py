import pytest
import sys
import os

# Add current directory to the import path so Python can find app.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import app as flask_app
from database import add_user

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def test_user():
    add_user("TESTUSER", "test123")
    return "TESTUSER", "test123"

@pytest.fixture(scope="function")
def admin_user():
    add_user("ADMIN", "admin")
    return "ADMIN", "admin"
