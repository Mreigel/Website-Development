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
    is_from_admin = db.Column(db.Boolean, default=False)
    thread_id = db.Column(db.Integer, index=True)
    context = db.Column(db.String(64), default='inquiry')

    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.Text)
    image = db.Column(db.Text)
    github_link = db.Column(db.Text)
    live_demo_link = db.Column(db.Text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    full_name = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.Text)
    country = db.Column(db.Text)

    # Encrypted fields
    _address = db.Column("address", db.Text)
    _email = db.Column("email", db.Text, unique=True)

    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def address(self):
        try:
            return decrypt_field(self._address) if self._address else None
        except Exception:
            return "[Invalid Address]"

    @address.setter
    def address(self, value):
        self._address = encrypt_field(value) if value else None

    @property
    def email(self):
        try:
            return decrypt_field(self._email) if self._email else None
        except Exception:
            return "[Invalid Email]"

    @email.setter
    def email(self, value):
        self._email = encrypt_field(value) if value else None
