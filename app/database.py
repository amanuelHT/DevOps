import sqlite3
import hashlib
import datetime
import os
import psycopg2
from urllib.parse import urlparse

user_db_file_location = "database_file/users.db"
note_db_file_location = "database_file/notes.db"
image_db_file_location = "database_file/images.db"


# Detect Postgres
DB_URL = os.getenv("DB_URL")
IS_POSTGRES = DB_URL is not None and DB_URL.startswith("postgresql://")

def get_connection(db_file=None):
    if IS_POSTGRES:
        parsed = urlparse(DB_URL)
        return psycopg2.connect(
            dbname=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
    else:
        return sqlite3.connect(db_file)



def list_users():
    _conn = sqlite3.connect(user_db_file_location)
    _c = _conn.cursor()

    _c.execute("SELECT id FROM users;")
    result = [x[0] for x in _c.fetchall()]

    _conn.close()
    
    return result

def verify(id, pw):
    _conn = sqlite3.connect(user_db_file_location)
    _c = _conn.cursor()

    _c.execute("SELECT pw FROM users WHERE id = '" + id + "';")
    result = _c.fetchone()[0] == hashlib.sha256(pw.encode()).hexdigest()
    
    _conn.close()

    return result

def delete_user_from_db(id):
    _conn = get_connection(user_db_file_location)
    _c = _conn.cursor()
    placeholder = "%s" if IS_POSTGRES else "?"
    _c.execute(f"DELETE FROM users WHERE id = {placeholder};", (id,))
    _conn.commit()
    _conn.close()

    _conn = get_connection(note_db_file_location)
    _c = _conn.cursor()
    _c.execute(f"DELETE FROM notes WHERE user = {placeholder};", (id,))
    _conn.commit()
    _conn.close()

    _conn = get_connection(image_db_file_location)
    _c = _conn.cursor()
    _c.execute(f"DELETE FROM images WHERE owner = {placeholder};", (id,))
    _conn.commit()
    _conn.close()


def add_user(id, pw):
    _conn = get_connection(user_db_file_location)
    _c = _conn.cursor()
    placeholder = "%s" if IS_POSTGRES else "?"
    _c.execute(f"INSERT INTO users VALUES({placeholder}, {placeholder});",
               (id.upper(), hashlib.sha256(pw.encode()).hexdigest()))
    _conn.commit()
    _conn.close()


def read_note_from_db(id):
    _conn = get_connection(note_db_file_location)
    _c = _conn.cursor()
    placeholder = "%s" if IS_POSTGRES else "?"
    _c.execute(f"SELECT note_id, timestamp, note FROM notes WHERE user = {placeholder};", (id.upper(),))
    result = _c.fetchall()
    _conn.close()
    return result



def delete_note_from_db(note_id):
    _conn = get_connection(note_db_file_location)
    _c = _conn.cursor()
    placeholder = "%s" if IS_POSTGRES else "?"
    _c.execute(f"DELETE FROM notes WHERE note_id = {placeholder};", (note_id,))
    _conn.commit()
    _conn.close()


    return result

def match_user_id_with_note_id(note_id):
    # Given the note id, confirm if the current user is the owner of the note which is being operated.
    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()

    command = "SELECT user FROM notes WHERE note_id = '" + note_id + "';" 
    _c.execute(command)
    result = _c.fetchone()[0]

    _conn.commit()
    _conn.close()

    return result

def write_note_into_db(id, note_to_write):
    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()

    current_timestamp = str(datetime.datetime.now())
    _c.execute("INSERT INTO notes values(?, ?, ?, ?)", (id.upper(), current_timestamp, note_to_write, hashlib.sha1((id.upper() + current_timestamp).encode()).hexdigest()))

    _conn.commit()
    _conn.close()

def delete_note_from_db(note_id):
    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()

    _c.execute("DELETE FROM notes WHERE note_id = ?;", (note_id))

    _conn.commit()
    _conn.close()

def image_upload_record(uid, owner, image_name, timestamp):
    _conn = get_connection(image_db_file_location)
    _c = _conn.cursor()
    placeholder = "%s" if IS_POSTGRES else "?"
    _c.execute(
        f"INSERT INTO images VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
        (uid, owner, image_name, timestamp)
    )
    _conn.commit()
    _conn.close()


def list_images_for_user(owner):
    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()

    command = "SELECT uid, timestamp, name FROM images WHERE owner = '{0}'".format(owner)
    _c.execute(command)
    result = _c.fetchall()

    _conn.commit()
    _conn.close()

    return result

def match_user_id_with_image_uid(image_uid):
    # Given the note id, confirm if the current user is the owner of the note which is being operated.
    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()

    command = "SELECT owner FROM images WHERE uid = '" + image_uid + "';" 
    _c.execute(command)
    result = _c.fetchone()[0]

    _conn.commit()
    _conn.close()

    return result

def delete_image_from_db(image_uid):
    _conn = get_connection(image_db_file_location)
    _c = _conn.cursor()
    placeholder = "%s" if IS_POSTGRES else "?"
    _c.execute(f"DELETE FROM images WHERE uid = {placeholder};", (image_uid,))
    _conn.commit()
    _conn.close()








if __name__ == "__main__":
    print(list_users())
