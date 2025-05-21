import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from werkzeug.utils import secure_filename
from config import get_config

from database import (
    list_users, verify, delete_user_from_db, add_user,
    read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id,
    image_upload_record, list_images_for_user, match_user_id_with_image_uid, delete_image_from_db
)

app = Flask(__name__)
app.config.from_object(get_config())

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Error Handlers
@app.errorhandler(401)
def unauthorized(e): return render_template("page_401.html"), 401

@app.errorhandler(403)
def forbidden(e): return render_template("page_403.html"), 403

@app.errorhandler(404)
def not_found(e): return render_template("page_404.html"), 404

@app.errorhandler(405)
def method_not_allowed(e): return render_template("page_405.html"), 405

@app.errorhandler(413)
def request_entity_too_large(e): return render_template("page_413.html"), 413

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/public/")
def public():
    return render_template("public_page.html")

@app.route("/private/")
def private():
    if "current_user" in session:
        notes = read_note_from_db(session['current_user'])
        notes_table = zip([n[0] for n in notes], [n[1] for n in notes], [n[2] for n in notes], ["/delete_note/" + n[0] for n in notes])
        
        images = list_images_for_user(session['current_user'])
        images_table = zip([i[0] for i in images], [i[1] for i in images], [i[2] for i in images], ["/delete_image/" + i[0] for i in images])
        
        return render_template("private_page.html", notes=notes_table, images=images_table)
    return abort(401)

@app.route("/admin/")
def admin():
    if session.get("current_user") == "ADMIN":
        users = list_users()
        user_table = zip(range(1, len(users)+1), users, ["/delete_user/" + u for u in users])
        return render_template("admin.html", users=user_table)
    return abort(401)

@app.route("/write_note", methods=["POST"])
def write_note():
    text = request.form.get("text_note_to_take")
    write_note_into_db(session['current_user'], text)
    return redirect(url_for("private"))

@app.route("/delete_note/<note_id>")
def delete_note(note_id):
    if session.get("current_user") == match_user_id_with_note_id(note_id):
        delete_note_from_db(note_id)
        return redirect(url_for("private"))
    return abort(401)

@app.route("/upload_image", methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('No selected file', category='danger')
        return redirect(url_for("private"))
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_time = str(datetime.datetime.now())
        uid = hashlib.sha1((upload_time + filename).encode()).hexdigest()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uid + "-" + filename)
        file.save(file_path)
        image_upload_record(uid, session['current_user'], filename, upload_time)
    return redirect(url_for("private"))

@app.route("/delete_image/<image_uid>")
def delete_image(image_uid):
    if session.get("current_user") == match_user_id_with_image_uid(image_uid):
        delete_image_from_db(image_uid)
        image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(image_uid)]
        for f in image_files:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
        return redirect(url_for("private"))
    return abort(401)

@app.route("/login", methods=["POST"])
def login():
    uid = request.form.get("id").upper()
    if uid in list_users() and verify(uid, request.form.get("pw")):
        session['current_user'] = uid
    return redirect(url_for("index"))

@app.route("/logout/")
def logout():
    print(f"👋 Logging out {session.get('current_user')}")
    session.pop("current_user", None)
    return redirect(url_for("index"))

@app.route("/delete_user/<id>/")
def delete_user(id):
    if session.get("current_user") == "ADMIN" and id != "ADMIN":
        for img in [i[0] for i in list_images_for_user(id)]:
            file = next((f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(img)), None)
            if file:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
        delete_user_from_db(id)
        return redirect(url_for("admin"))
    return abort(401)

@app.route("/add_user", methods=["POST"])
def add_user_route():
    if session.get("current_user") != "ADMIN":
        return abort(401)
    
    uid = request.form.get('id').upper()
    pw = request.form.get('pw')
    if uid in list_users():
        flash("User already exists", category="danger")
    elif " " in uid or "'" in uid:
        flash("Invalid characters in user ID", category="danger")
    else:
        add_user(uid, pw)
        flash("User added", category="success")
    return redirect(url_for("admin"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
