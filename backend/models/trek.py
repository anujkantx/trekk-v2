from datetime import datetime, date
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

    # DB constraints to guarantee non-negative inventory and prevent overbooking
    __table_args__ = (
        db.CheckConstraint("available_slots >= 0", name="check_min_available_slots"),
        db.CheckConstraint("total_slots >= available_slots", name="check_slots_capacity"),
    )

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

    @staticmethod
    def parse_date(val):
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            try:
                return datetime.strptime(val.strip(), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None
        return None

    @staticmethod
    def validate_data(data, existing_trek=None):
        if not data or not isinstance(data, dict):
            return False, "JSON body is required", None

        # Check required fields on creation
        if existing_trek is None:
            required = ["name", "location", "total_slots", "start_date", "end_date"]
            missing = [f for f in required if f not in data or data[f] is None or data[f] == ""]
            if missing:
                return False, f"Missing required fields: {', '.join(missing)}", None

        name = data.get("name", existing_trek.name if existing_trek else "").strip()
        location = data.get("location", existing_trek.location if existing_trek else "").strip()
        difficulty = data.get("difficulty", existing_trek.difficulty if existing_trek else "Moderate").strip().capitalize()
        duration_days = data.get("duration_days", existing_trek.duration_days if existing_trek else 1)
        description = data.get("description", existing_trek.description if existing_trek else None)
        status = data.get("status", existing_trek.status if existing_trek else "Open").strip().capitalize()

        if not name:
            return False, "Trek name is required", None
        if not location:
            return False, "Trek location is required", None

        # Price validation
        price_raw = data.get("price", existing_trek.price if existing_trek else 0.0)
        try:
            price = float(price_raw)
            if price < 0:
                return False, "Price must be a non-negative number", None
        except (ValueError, TypeError):
            return False, "Price must be a valid number", None

        # Total slots validation
        slots_raw = data.get("total_slots", existing_trek.total_slots if existing_trek else None)
        if not isinstance(slots_raw, int) or slots_raw <= 0:
            return False, "total_slots must be a positive integer", None
        total_slots = slots_raw

        # Dates validation using Trek.parse_date
        start_date = Trek.parse_date(data["start_date"]) if "start_date" in data else (existing_trek.start_date if existing_trek else None)
        end_date = Trek.parse_date(data["end_date"]) if "end_date" in data else (existing_trek.end_date if existing_trek else None)

        if not start_date or not end_date:
            return False, "Valid start_date and end_date (YYYY-MM-DD) are required", None

        if start_date > end_date:
            return False, "start_date cannot be after end_date", None

        if existing_trek is None and start_date < date.today():
            return False, "start_date cannot be in the past", None

        valid_difficulties = {"Easy", "Moderate", "Hard"}
        if difficulty not in valid_difficulties:
            return False, f"Difficulty must be one of: {list(valid_difficulties)}", None

        valid_statuses = {"Pending", "Approved", "Open", "Closed", "Completed"}
        if status not in valid_statuses:
            return False, f"Status must be one of: {list(valid_statuses)}", None

        if not isinstance(duration_days, int) or duration_days <= 0:
            return False, "duration_days must be a positive integer", None

        available_slots = total_slots
        if existing_trek is not None:
            booked_slots = existing_trek.total_slots - existing_trek.available_slots
            if total_slots < booked_slots:
                return False, f"Cannot reduce total slots below existing booked count ({booked_slots})", None
            available_slots = total_slots - booked_slots

        cleaned = {
            "name": name,
            "location": location,
            "difficulty": difficulty,
            "duration_days": duration_days,
            "total_slots": total_slots,
            "available_slots": available_slots,
            "price": price,
            "description": description.strip() if description else None,
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        }

        return True, None, cleaned
