import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from database import (
    list_users, verify, delete_user_from_db, add_user,
    read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id,
    image_upload_record, list_images_for_user, match_user_id_with_image_uid, delete_image_from_db
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']  # ensure sessions and flashes work

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413


@app.route("/")
def FUN_root():
    return render_template("index.html")

@app.route("/public/")
def FUN_public():
    return render_template("public_page.html")

@app.route("/private/")
def FUN_private():
    if "current_user" in session:
        user = session['current_user']
        notes_list = read_note_from_db(user)
        notes_table = zip(
            [x[0] for x in notes_list],
            [x[1] for x in notes_list],
            [x[2] for x in notes_list],
            [f"/delete_note/{x[0]}" for x in notes_list]
        )

        images_list = list_images_for_user(user)
        images_table = zip(
            [x[0] for x in images_list],
            [x[1] for x in images_list],
            [x[2] for x in images_list],
            [f"/delete_image/{x[0]}" for x in images_list]
        )

        return render_template("private_page.html", notes=notes_table, images=images_table)
    else:
        return abort(401)

@app.route("/admin/")
def FUN_admin():
    if session.get("current_user") == "ADMIN":
        user_list = list_users()
        user_table = zip(
            range(1, len(user_list) + 1),
            user_list,
            [f"/delete_user/{u}" for u in user_list]
        )
        return render_template("admin.html", users=user_table)
    else:
        return abort(401)


@app.route("/write_note", methods=["POST"])
def FUN_write_note():
    text_to_write = request.form.get("text_note_to_take") or ""
    write_note_into_db(session['current_user'], text_to_write)
    return redirect(url_for("FUN_private"))

@app.route("/delete_note/<note_id>", methods=["GET"])
def FUN_delete_note(note_id):
    if session.get("current_user") == match_user_id_with_note_id(note_id):
        delete_note_from_db(note_id)
    else:
        return abort(401)
    return redirect(url_for("FUN_private"))


@app.route("/upload_image", methods=['POST'])
def FUN_upload_image():
    if 'file' not in request.files:
        flash('No file part', category='danger')
        return redirect(url_for("FUN_private"))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', category='danger')
        return redirect(url_for("FUN_private"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_time = datetime.datetime.utcnow().isoformat()
        image_uid = hashlib.sha1((upload_time + filename).encode()).hexdigest()
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{image_uid}-{filename}")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(save_path)
        image_upload_record(image_uid, session['current_user'], filename, upload_time)
    return redirect(url_for("FUN_private"))

@app.route("/delete_image/<image_uid>", methods=["GET"])
def FUN_delete_image(image_uid):
    if session.get("current_user") == match_user_id_with_image_uid(image_uid):
        delete_image_from_db(image_uid)
        pool = app.config['UPLOAD_FOLDER']
        for fname in os.listdir(pool):
            if fname.startswith(f"{image_uid}-"):
                os.remove(os.path.join(pool, fname))
                break
    else:
        return abort(401)
    return redirect(url_for("FUN_private"))


@app.route("/login", methods=["POST"])
def FUN_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Username and password are required.", category="danger")
        return redirect(url_for("FUN_root"))

    user_id = username.upper()
    if user_id in list_users() and verify(user_id, password):
        session["current_user"] = user_id

    return redirect(url_for("FUN_root"))

@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return redirect(url_for("FUN_root"))


@app.route("/delete_user/<id>/", methods=['GET'])
def FUN_delete_user(id):
    if session.get("current_user") == "ADMIN":
        if id == "ADMIN":
            return abort(403)
        # Remove images
        for uid, _, _ in list_images_for_user(id):
            pool = app.config['UPLOAD_FOLDER']
            for fname in os.listdir(pool):
                if fname.startswith(f"{uid}-"):
                    os.remove(os.path.join(pool, fname))
                    break
        delete_user_from_db(id)
        return redirect(url_for("FUN_admin"))
    else:
        return abort(401)

@app.route("/add_user", methods=["POST"])
def FUN_add_user():
    if session.get("current_user") != "ADMIN":
        return abort(401)

    new_id = request.form.get('id')
    new_pw = request.form.get('pw')
    if not new_id or not new_pw:
        flash("User ID and password are required.", category="danger")
    elif new_id.upper() in list_users():
        flash("User ID already exists.", category="danger")
    elif " " in new_id or "'" in new_id:
        flash("Invalid characters in User ID.", category="danger")
    else:
        add_user(new_id, new_pw)
        return redirect(url_for("FUN_admin"))

    # On error, re-render admin page with messages
    user_list = list_users()
    user_table = zip(range(1, len(user_list)+1), user_list, [f"/delete_user/{u}" for u in user_list])
    return render_template("admin.html", users=user_table)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
