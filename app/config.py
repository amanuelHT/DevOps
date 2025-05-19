import os
import sqlite3
import hashlib
import datetime
from urllib.parse import urlparse

import psycopg2

from config import DATABASE_URL

# Determine whether to use Postgres or SQLite
USE_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")


def get_connection(db_key='users'):
    """
    Return a database connection based on environment.
    Uses Postgres when DATABASE_URL is set to a postgres URI,
    otherwise falls back to local SQLite files.
    """
    if USE_POSTGRES:
        result = urlparse(DATABASE_URL)
        return psycopg2.connect(
            dbname=result.path.lstrip("/"),
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
    else:
        paths = {
            'users':  'database_file/users.db',
            'notes':  'database_file/notes.db',
            'images': 'database_file/images.db'
        }
        return sqlite3.connect(paths[db_key])


def list_users():
    conn = get_connection('users')
    cur = conn.cursor()
    cur.execute('SELECT id FROM users;')
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users


def verify(user_id, pw):
    conn = get_connection('users')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('SELECT pw FROM users WHERE id = %s;', (user_id.upper(),))
    else:
        cur.execute('SELECT pw FROM users WHERE id = ?;', (user_id.upper(),))
    row = cur.fetchone()
    conn.close()
    return bool(row and row[0] == hashlib.sha256(pw.encode()).hexdigest())


def add_user(user_id, pw):
    conn = get_connection('users')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute(
            'INSERT INTO users (id, pw) VALUES (%s, %s);',
            (user_id.upper(), hashlib.sha256(pw.encode()).hexdigest())
        )
    else:
        cur.execute(
            'INSERT INTO users VALUES (?, ?);',
            (user_id.upper(), hashlib.sha256(pw.encode()).hexdigest())
        )
    conn.commit()
    conn.close()


def delete_user_from_db(user_id):
    # Delete user record
    conn = get_connection('users')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('DELETE FROM users WHERE id = %s;', (user_id.upper(),))
    else:
        cur.execute('DELETE FROM users WHERE id = ?;', (user_id.upper(),))
    conn.commit()
    conn.close()

    # Delete related notes
    conn = get_connection('notes')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('DELETE FROM notes WHERE user = %s;', (user_id.upper(),))
    else:
        cur.execute('DELETE FROM notes WHERE user = ?;', (user_id.upper(),))
    conn.commit()
    conn.close()

    # Delete related images
    conn = get_connection('images')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('DELETE FROM images WHERE owner = %s;', (user_id.upper(),))
    else:
        cur.execute('DELETE FROM images WHERE owner = ?;', (user_id.upper(),))
    conn.commit()
    conn.close()


def read_notes(user_id):
    conn = get_connection('notes')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute(
            'SELECT note_id, timestamp, note FROM notes WHERE user = %s;', 
            (user_id.upper(),)
        )
    else:
        cur.execute(
            'SELECT note_id, timestamp, note FROM notes WHERE user = ?;', 
            (user_id.upper(),)
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def match_user_id_with_note_id(note_id):
    conn = get_connection('notes')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('SELECT user FROM notes WHERE note_id = %s;', (note_id,))
    else:
        cur.execute('SELECT user FROM notes WHERE note_id = ?;', (note_id,))
    owner = cur.fetchone()[0]
    conn.close()
    return owner


def write_note(user_id, note_text):
    conn = get_connection('notes')
    cur = conn.cursor()
    ts = datetime.datetime.now().isoformat()
    note_id = hashlib.sha1(f"{user_id.upper()}{ts}".encode()).hexdigest()
    if USE_POSTGRES:
        cur.execute(
            'INSERT INTO notes (user, timestamp, note, note_id) VALUES (%s, %s, %s, %s);',
            (user_id.upper(), ts, note_text, note_id)
        )
    else:
        cur.execute(
            'INSERT INTO notes VALUES (?, ?, ?, ?);',
            (user_id.upper(), ts, note_text, note_id)
        )
    conn.commit()
    conn.close()
    return note_id


def delete_note(note_id):
    conn = get_connection('notes')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('DELETE FROM notes WHERE note_id = %s;', (note_id,))
    else:
        cur.execute('DELETE FROM notes WHERE note_id = ?;', (note_id,))
    conn.commit()
    conn.close()


def image_upload_record(uid, owner, image_name, timestamp):
    conn = get_connection('images')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute(
            'INSERT INTO images (uid, owner, name, timestamp) VALUES (%s, %s, %s, %s);',
            (uid, owner, image_name, timestamp)
        )
    else:
        cur.execute(
            'INSERT INTO images VALUES (?, ?, ?, ?);',
            (uid, owner, image_name, timestamp)
        )
    conn.commit()
    conn.close()


def list_images_for_user(owner):
    # Wrapper for backward compatibility
    conn = get_connection('images')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('SELECT uid, timestamp, name FROM images WHERE owner = %s;', (owner,))
    else:
        cur.execute('SELECT uid, timestamp, name FROM images WHERE owner = ?;', (owner,))
    rows = cur.fetchall()
    conn.close()
    return rows


def match_user_id_with_image_uid(image_uid):
    conn = get_connection('images')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('SELECT owner FROM images WHERE uid = %s;', (image_uid,))
    else:
        cur.execute('SELECT owner FROM images WHERE uid = ?;', (image_uid,))
    owner = cur.fetchone()[0]
    conn.close()
    return owner


def delete_image_from_db(image_uid):
    # Wrapper for backward compatibility
    conn = get_connection('images')
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute('DELETE FROM images WHERE uid = %s;', (image_uid,))
    else:
        cur.execute('DELETE FROM images WHERE uid = ?;', (image_uid,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    print(list_users())
