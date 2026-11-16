from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user") # 'admin', 'staff', 'user'
    status = db.Column(db.String(20), nullable=False, default="active") # 'active', 'blacklisted'
    contact_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    assigned_treks = db.relationship("Trek", back_populates="assigned_staff")

    def __init__(self, username, email, role="user", status="active", contact_number=None, password_hash=""):
        self.username = username
        self.email = email
        self.role = role
        self.status = status
        self.contact_number = contact_number
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "contact_number": self.contact_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
