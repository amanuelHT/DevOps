import datetime
import hashlib
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Text, primary_key=True)
    pw = db.Column(db.Text, nullable=False)

class Note(db.Model):
    __tablename__ = "notes"
    user      = db.Column(db.Text, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    note      = db.Column(db.Text, nullable=False)
    note_id   = db.Column(db.Text, primary_key=True)

class Image(db.Model):
    __tablename__ = "images"
    uid       = db.Column(db.Text, primary_key=True)
    owner     = db.Column(db.Text, db.ForeignKey("users.id"), nullable=False)
    name      = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
