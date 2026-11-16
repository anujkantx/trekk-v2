from datetime import datetime, date
from backend.extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    num_slots = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default="Booked") # 'Booked', 'Cancelled', 'Completed'
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")

    def __init__(self, user_id, trek_id, num_slots=1, status="Booked"):
        self.user_id = user_id
        self.trek_id = trek_id
        self.num_slots = num_slots
        self.status = status

    def to_dict(self):
        can_cancel = False
        if self.status == "Booked" and self.trek and self.trek.start_date:
            can_cancel = (self.trek.start_date > date.today())

        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.name if self.trek else None,
            "trek_location": self.trek.location if self.trek else None,
            "trek_start_date": self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            "trek_end_date": self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
            "num_slots": self.num_slots,
            "status": self.status,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "can_cancel": can_cancel
        }
