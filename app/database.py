import os
import hashlib
import datetime

USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES:
    import psycopg2
else:
    import sqlite3

user_db_file_location = "database_file/users.db"
note_db_file_location = "database_file/notes.db"
image_db_file_location = "database_file/images.db"

def get_connection(db_type):
    print(f"📡 Connecting to {'PostgreSQL' if USE_POSTGRES else 'SQLite'} for {db_type}")
    if USE_POSTGRES:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
    else:
        conn = sqlite3.connect(f"database_file/{db_type}.db")
    print("✅ DB connection established")
    return conn

def list_users():
    print("🔍 Running list_users()")
    _conn = get_connection("users")
    _c = _conn.cursor()
    _c.execute("SELECT id FROM users;")
    result = [x[0] for x in _c.fetchall()]
    _conn.close()
    print(f"✅ list_users(): {result}")
    return result

def verify(id, pw):
    print(f"🔐 Verifying user: {id}")
    _conn = get_connection("users")
    _c = _conn.cursor()
    _c.execute("SELECT pw FROM users WHERE id = %s;" if USE_POSTGRES else "SELECT pw FROM users WHERE id = ?;", (id,))
    result = _c.fetchone()[0] == hashlib.sha256(pw.encode()).hexdigest()
    _conn.close()
    print(f"✅ Password verified: {result}")
    return result

def delete_user_from_db(id):
    print(f"🗑️ Deleting user: {id}")
    _conn = get_connection("users")
    _c = _conn.cursor()
    _c.execute("DELETE FROM users WHERE id = %s;" if USE_POSTGRES else "DELETE FROM users WHERE id = ?;", (id,))
    _conn.commit()
    _conn.close()

    _conn = get_connection("notes")
    _c = _conn.cursor()
    _c.execute("DELETE FROM notes WHERE user = %s;" if USE_POSTGRES else "DELETE FROM notes WHERE user = ?;", (id,))
    _conn.commit()
    _conn.close()

    _conn = get_connection("images")
    _c = _conn.cursor()
    _c.execute("DELETE FROM images WHERE owner = %s;" if USE_POSTGRES else "DELETE FROM images WHERE owner = ?;", (id,))
    _conn.commit()
    _conn.close()

def add_user(id, pw):
    print(f"➕ Adding user: {id}")
    _conn = get_connection("users")
    _c = _conn.cursor()
    _c.execute("INSERT INTO users values(%s, %s)" if USE_POSTGRES else "INSERT INTO users values(?, ?)",
               (id.upper(), hashlib.sha256(pw.encode()).hexdigest()))
    _conn.commit()
    _conn.close()

def read_note_from_db(id):
    print(f"📓 Reading notes for: {id}")
    _conn = get_connection("notes")
    _c = _conn.cursor()
    _c.execute("SELECT note_id, timestamp, note FROM notes WHERE user = %s;" if USE_POSTGRES else "SELECT note_id, timestamp, note FROM notes WHERE user = ?;", (id.upper(),))
    result = _c.fetchall()
    _conn.commit()
    _conn.close()
    return result

def match_user_id_with_note_id(note_id):
    _conn = get_connection("notes")
    _c = _conn.cursor()
    _c.execute("SELECT user FROM notes WHERE note_id = %s;" if USE_POSTGRES else "SELECT user FROM notes WHERE note_id = ?;", (note_id,))
    result = _c.fetchone()[0]
    _conn.commit()
    _conn.close()
    return result

def write_note_into_db(id, note_to_write):
    print(f"📝 Writing note for user: {id}")
    _conn = get_connection("notes")
    _c = _conn.cursor()
    current_timestamp = str(datetime.datetime.now())
    note_id = hashlib.sha1((id.upper() + current_timestamp).encode()).hexdigest()
    _c.execute("INSERT INTO notes values(%s, %s, %s, %s)" if USE_POSTGRES else "INSERT INTO notes values(?, ?, ?, ?)",
               (id.upper(), current_timestamp, note_to_write, note_id))
    _conn.commit()
    _conn.close()

def delete_note_from_db(note_id):
    print(f"❌ Deleting note: {note_id}")
    _conn = get_connection("notes")
    _c = _conn.cursor()
    _c.execute("DELETE FROM notes WHERE note_id = %s;" if USE_POSTGRES else "DELETE FROM notes WHERE note_id = ?;", (note_id,))
    _conn.commit()
    _conn.close()

def image_upload_record(uid, owner, image_name, timestamp):
    print(f"📸 Uploading image for user: {owner}")
    _conn = get_connection("images")
    _c = _conn.cursor()
    _c.execute("INSERT INTO images VALUES (%s, %s, %s, %s)" if USE_POSTGRES else "INSERT INTO images VALUES (?, ?, ?, ?)",
               (uid, owner, image_name, timestamp))
    _conn.commit()
    _conn.close()

def list_images_for_user(owner):
    print(f"🖼️ Listing images for: {owner}")
    _conn = get_connection("images")
    _c = _conn.cursor()
    _c.execute("SELECT uid, timestamp, name FROM images WHERE owner = %s" if USE_POSTGRES else "SELECT uid, timestamp, name FROM images WHERE owner = ?", (owner,))
    result = _c.fetchall()
    _conn.commit()
    _conn.close()
    return result

def match_user_id_with_image_uid(image_uid):
    _conn = get_connection("images")
    _c = _conn.cursor()
    _c.execute("SELECT owner FROM images WHERE uid = %s;" if USE_POSTGRES else "SELECT owner FROM images WHERE uid = ?;", (image_uid,))
    result = _c.fetchone()[0]
    _conn.commit()
    _conn.close()
    return result

def delete_image_from_db(image_uid):
    print(f"🧹 Deleting image with UID: {image_uid}")
    _conn = get_connection("images")
    _c = _conn.cursor()
    _c.execute("DELETE FROM images WHERE uid = %s;" if USE_POSTGRES else "DELETE FROM images WHERE uid = ?;", (image_uid,))
    _conn.commit()
    _conn.close()

if __name__ == "__main__":
    print(list_users())
