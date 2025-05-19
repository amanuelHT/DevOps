import os
import sqlite3
import hashlib
import datetime
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import RealDictCursor

from config import DATABASE_URL

# Determine whether to use Postgres or SQLite
USE_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")

def get_connection(db_key="users"):
    """
    Return a DB connection.
    - If USE_POSTGRES is True, parse DATABASE_URL and connect via psycopg2.
    - Otherwise, connect to local SQLite at the appropriate path.
    """
    if USE_POSTGRES:
        result = urlparse(DATABASE_URL)
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432
        dbname = result.path.lstrip("/")

        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    else:
        paths = {
            "users":  "database_file/users.db",
            "notes":  "database_file/notes.db",
            "images": "database_file/images.db"
        }
        return sqlite3.connect(paths[db_key])

def list_users():
    conn = get_connection("users")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users;")
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users

def verify(user_id, pw):
    conn = get_connection("users")
    cur = conn.cursor()
    query = "SELECT pw FROM users WHERE id = %s;" if USE_POSTGRES else \
            "SELECT pw FROM users WHERE id = ?;"
    params = (user_id.upper(),)
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    stored_hash = row[0]
    return stored_hash == hashlib.sha256(pw.encode()).hexdigest()

def add_user(user_id, pw):
    conn = get_connection("users")
    cur = conn.cursor()
    query = "INSERT INTO users (id, pw) VALUES (%s, %s);" if USE_POSTGRES else \
            "INSERT INTO users VALUES (?, ?);"
    params = (user_id.upper(), hashlib.sha256(pw.encode()).hexdigest())
    cur.execute(query, params)
    conn.commit()
    conn.close()

def delete_user_from_db(user_id):
    # Delete from users
    conn = get_connection("users")
    cur = conn.cursor()
    query = "DELETE FROM users WHERE id = %s;" if USE_POSTGRES else \
            "DELETE FROM users WHERE id = ?;"
    cur.execute(query, (user_id.upper(),))
    conn.commit()
    conn.close()

    # Delete related notes
    conn = get_connection("notes")
    cur = conn.cursor()
    query = "DELETE FROM notes WHERE user = %s;" if USE_POSTGRES else \
            "DELETE FROM notes WHERE user = ?;"
    cur.execute(query, (user_id.upper(),))
    conn.commit()
    conn.close()

    # Delete related images
    conn = get_connection("images")
    cur = conn.cursor()
    query = "DELETE FROM images WHERE owner = %s;" if USE_POSTGRES else \
            "DELETE FROM images WHERE owner = ?;"
    cur.execute(query, (user_id.upper(),))
    conn.commit()
    conn.close()

def read_notes(user_id):
    conn = get_connection("notes")
    cur = conn.cursor()
    query = ("SELECT note_id, timestamp, note FROM notes "
             "WHERE user = %s;") if USE_POSTGRES else \
            "SELECT note_id, timestamp, note FROM notes WHERE user = ?;"
    cur.execute(query, (user_id.upper(),))
    notes = cur.fetchall()
    conn.close()
    return notes

def match_user_id_with_note_id(note_id):
    conn = get_connection("notes")
    cur = conn.cursor()
    query = "SELECT user FROM notes WHERE note_id = %s;" if USE_POSTGRES else \
            "SELECT user FROM notes WHERE note_id = ?;"
    cur.execute(query, (note_id,))
    owner = cur.fetchone()[0]
    conn.close()
    return owner

def write_note(user_id, note_text):
    conn = get_connection("notes")
    cur = conn.cursor()
    ts = datetime.datetime.now().isoformat()
    note_id = hashlib.sha1(f"{user_id.upper()}{ts}".encode()).hexdigest()
    query = ("INSERT INTO notes (user, timestamp, note, note_id) "
             "VALUES (%s, %s, %s, %s);") if USE_POSTGRES else \
            "INSERT INTO notes VALUES (?, ?, ?, ?);"
    cur.execute(query, (user_id.upper(), ts, note_text, note_id))
    conn.commit()
    conn.close()
    return note_id

def delete_note(note_id):
    conn = get_connection("notes")
    cur = conn.cursor()
    query = "DELETE FROM notes WHERE note_id = %s;" if USE_POSTGRES else \
            "DELETE FROM notes WHERE note_id = ?;"
    cur.execute(query, (note_id,))
    conn.commit()
    conn.close()

def list_images(owner):
    conn = get_connection("images")
    cur = conn.cursor()
    query = ("SELECT uid, timestamp, name FROM images "
             "WHERE owner = %s;") if USE_POSTGRES else \
            "SELECT uid, timestamp, name FROM images WHERE owner = ?;"
    cur.execute(query, (owner,))
    imgs = cur.fetchall()
    conn.close()
    return imgs

def match_user_id_with_image_uid(image_uid):
    conn = get_connection("images")
    cur = conn.cursor()
    query = "SELECT owner FROM images WHERE uid = %s;" if USE_POSTGRES else \
            "SELECT owner FROM images WHERE uid = ?;"
    cur.execute(query, (image_uid,))
    owner = cur.fetchone()[0]
    conn.close()
    return owner

def delete_image(image_uid):
    conn = get_connection("images")
    cur = conn.cursor()
    query = "DELETE FROM images WHERE uid = %s;" if USE_POSTGRES else \
            "DELETE FROM images WHERE uid = ?;"
    cur.execute(query, (image_uid,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Quick sanity check
    print(list_users())
