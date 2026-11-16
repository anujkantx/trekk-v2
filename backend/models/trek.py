from datetime import datetime
from backend.extensions import db

class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, default="Moderate") # 'Easy', 'Moderate', 'Hard'
    duration_days = db.Column(db.Integer, nullable=False, default=1)
    total_slots = db.Column(db.Integer, nullable=False, default=20)
    available_slots = db.Column(db.Integer, nullable=False, default=20)
    price = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending") # 'Pending', 'Approved', 'Open', 'Closed', 'Completed'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key linking to assigned staff (User)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    assigned_staff = db.relationship("User", back_populates="assigned_treks")
    bookings = db.relationship("Booking", back_populates="trek", cascade="all, delete-orphan")

    def __init__(self, name, location, difficulty="Moderate", duration_days=1, total_slots=20, 
                 available_slots=20, price=0.0, description=None, status="Pending", 
                 start_date=None, end_date=None, assigned_staff_id=None):
        self.name = name
        self.location = location
        self.difficulty = difficulty
        self.duration_days = duration_days
        self.total_slots = total_slots
        self.available_slots = available_slots
        self.price = price
        self.description = description
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.assigned_staff_id = assigned_staff_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty,
            "duration_days": self.duration_days,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "price": self.price,
            "description": self.description,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff_name": self.assigned_staff.username if self.assigned_staff else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
