from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from encryption import encrypt_field, decrypt_field

db = SQLAlchemy()


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', backref='messages')


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(120))
    image = db.Column(db.String(120))
    github_link = db.Column(db.String(255))
    live_demo_link = db.Column(db.String(255))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120))

    # Expanded encrypted fields
    _address = db.Column("address", db.String(512))  # Increased from 256
    _email = db.Column("email", db.String(512), unique=True)  # Increased from 128

    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def address(self):
        return decrypt_field(self._address) if self._address else None

    @address.setter
    def address(self, value):
        self._address = encrypt_field(value) if value else None

    @property
    def email(self):
        return decrypt_field(self._email) if self._email else None

    @email.setter
    def email(self, value):
        self._email = encrypt_field(value) if value else None
