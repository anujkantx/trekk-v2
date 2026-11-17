from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.extensions import db, cache
from backend.models.trek import Trek
from backend.models.user import User
from backend.models.booking import Booking
from backend.utils.decorators import admin_required, staff_or_admin_required

treks_bp = Blueprint("treks", __name__, url_prefix="/api/treks")

VALID_DIFFICULTIES = {"Easy", "Moderate", "Hard"}
VALID_STATUSES = {"Pending", "Approved", "Open", "Closed", "Completed"}

def invalidate_trek_cache():
    try:
        cache.clear()
    except Exception:
        pass

def make_treks_cache_key(*args, **kwargs):
    scope = "public"
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user = db.session.get(User, int(identity))
            if user and user.status == "active":
                if user.role == "admin":
                    scope = "admin"
                elif user.role == "staff":
                    view = request.args.get("view", "assigned").strip().lower()
                    scope = "public" if view == "all" else f"staff_{user.id}"
    except Exception:
        pass
    query_string = request.query_string.decode("utf-8")
    return f"treks_list:{request.path}?{query_string}&_scope={scope}"

def make_trek_detail_cache_key(*args, **kwargs):
    scope = "public"
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user = db.session.get(User, int(identity))
            if user and user.status == "active":
                if user.role == "admin":
                    scope = "admin"
                elif user.role == "staff":
                    scope = f"staff_{user.id}"
    except Exception:
        pass
    return f"trek_detail:{request.path}&_scope={scope}"

@treks_bp.route("", methods=["GET"])
@cache.cached(timeout=300, make_cache_key=make_treks_cache_key)
def get_treks():
    query = Trek.query

    # Search by trek name or location
    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(
            (Trek.name.ilike(f"%{search}%")) | (Trek.location.ilike(f"%{search}%"))
        )

    # Filter by difficulty
    difficulty = request.args.get("difficulty", "").strip().capitalize()
    if difficulty in VALID_DIFFICULTIES:
        query = query.filter_by(difficulty=difficulty)

    # Price range filters
    min_price = request.args.get("min_price", type=float)
    if min_price is not None:
        query = query.filter(Trek.price >= min_price)

    max_price = request.args.get("max_price", type=float)
    if max_price is not None:
        query = query.filter(Trek.price <= max_price)

    # Status and visibility scoping based on role (verified against DB status)
    current_role = None
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user = db.session.get(User, int(identity))
            if user and user.status == "active":
                current_user_id = user.id
                current_role = user.role
    except Exception:
        pass

    requested_status = request.args.get("status", "").strip().capitalize()

    if current_role == "admin":
        # Admin sees all treks across the platform
        if requested_status in VALID_STATUSES:
            query = query.filter_by(status=requested_status)
        assigned_staff_id = request.args.get("assigned_staff_id", type=int)
        if assigned_staff_id:
            query = query.filter_by(assigned_staff_id=assigned_staff_id)

    elif current_role == "staff":
        # Staff sees their assigned treks by default (or public catalog if view=all)
        view = request.args.get("view", "assigned").strip().lower()
        if view == "all":
            query = query.filter(Trek.status.in_(["Approved", "Open"]))
            if requested_status in ["Approved", "Open"]:
                query = query.filter_by(status=requested_status)
        else:
            query = query.filter(Trek.assigned_staff_id == current_user_id)
            if requested_status in VALID_STATUSES:
                query = query.filter_by(status=requested_status)

    else:
        # Default user (registered trekker or guest): only Approved and Open treks
        if requested_status in ["Approved", "Open"]:
            query = query.filter_by(status=requested_status)
        else:
            query = query.filter(Trek.status.in_(["Approved", "Open"]))

    treks = query.order_by(Trek.start_date.asc()).all()

    return jsonify({
        "status": "success",
        "data": [trek.to_dict() for trek in treks]
    }), 200


@treks_bp.route("/<int:trek_id>", methods=["GET"])
@cache.cached(timeout=300, make_cache_key=make_trek_detail_cache_key)
def get_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    # If trek is Open or Approved, it is publicly visible
    if trek.status in ["Open", "Approved"]:
        return jsonify({
            "status": "success",
            "data": trek.to_dict()
        }), 200

    # For non-public statuses (Pending, Closed, Completed), verify permissions against DB
    current_role = None
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user = db.session.get(User, int(identity))
            if user and user.status == "active":
                current_user_id = user.id
                current_role = user.role
    except Exception:
        pass

    # Admin can view all; Staff can view only their assigned treks
    is_admin = current_role == "admin"
    is_assigned_staff = current_role == "staff" and trek.assigned_staff_id == current_user_id

    if not (is_admin or is_assigned_staff):
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    return jsonify({
        "status": "success",
        "data": trek.to_dict()
    }), 200


@treks_bp.route("", methods=["POST"])
@admin_required
def create_trek():
    data = request.get_json()
    is_valid, error, cleaned = Trek.validate_data(data)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400

    assigned_staff_id = data.get("assigned_staff_id")
    if assigned_staff_id:
        staff_user = db.session.get(User, assigned_staff_id)
        if not staff_user or staff_user.role != "staff":
            return jsonify({"status": "error", "message": "Assigned user must exist and have the 'staff' role"}), 400

    new_trek = Trek(
        name=cleaned["name"],
        location=cleaned["location"],
        difficulty=cleaned["difficulty"],
        duration_days=cleaned["duration_days"],
        total_slots=cleaned["total_slots"],
        available_slots=cleaned["available_slots"],
        price=cleaned["price"],
        description=cleaned["description"],
        status=cleaned["status"],
        start_date=cleaned["start_date"],
        end_date=cleaned["end_date"],
        assigned_staff_id=assigned_staff_id
    )

    db.session.add(new_trek)
    db.session.commit()
    invalidate_trek_cache()

    return jsonify({
        "status": "success",
        "message": "Trek created successfully",
        "data": new_trek.to_dict()
    }), 201


@treks_bp.route("/<int:trek_id>", methods=["PUT"])
@staff_or_admin_required
def update_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    # Staff can only edit treks assigned to them
    if current_role == "staff" and trek.assigned_staff_id != current_user_id:
        return jsonify({"status": "error", "message": "You can only modify treks assigned to you"}), 403

    data = request.get_json() or {}

    # Validate merged state using reusable model validator
    is_valid, error, cleaned = Trek.validate_data(data, existing_trek=trek)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400

    # Staff assignment check (admin only)
    if "assigned_staff_id" in data and current_role == "admin":
        staff_id = data["assigned_staff_id"]
        if staff_id:
            staff_user = db.session.get(User, staff_id)
            if not staff_user or staff_user.role != "staff":
                return jsonify({"status": "error", "message": "Assigned user must have 'staff' role"}), 400
            trek.assigned_staff_id = staff_id
        else:
            trek.assigned_staff_id = None

    # Date and status business guards
    new_status = cleaned["status"]
    if new_status == "Completed" and cleaned["start_date"] > date.today():
        return jsonify({"status": "error", "message": "Cannot mark trek as completed before its start date"}), 400

    if new_status == "Open" and cleaned["end_date"] < date.today():
        return jsonify({"status": "error", "message": "Cannot open a trek whose end date has passed"}), 400

    # Cascade: auto-complete active bookings when trek completes
    if new_status == "Completed" and trek.status != "Completed":
        active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
        for b in active_bookings:
            b.status = "Completed"

    # Apply validated changes
    trek.name = cleaned["name"]
    trek.location = cleaned["location"]
    trek.difficulty = cleaned["difficulty"]
    trek.duration_days = cleaned["duration_days"]
    trek.total_slots = cleaned["total_slots"]
    trek.available_slots = cleaned["available_slots"]
    trek.price = cleaned["price"]
    trek.description = cleaned["description"]
    trek.status = cleaned["status"]
    trek.start_date = cleaned["start_date"]
    trek.end_date = cleaned["end_date"]

    db.session.commit()
    invalidate_trek_cache()

    return jsonify({
        "status": "success",
        "message": "Trek updated successfully",
        "data": trek.to_dict()
    }), 200


@treks_bp.route("/<int:trek_id>/status", methods=["PATCH"])
@staff_or_admin_required
def update_trek_status(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    # Staff can only update their own trek's status
    if current_role == "staff" and trek.assigned_staff_id != current_user_id:
        return jsonify({"status": "error", "message": "You can only update status for treks assigned to you"}), 403

    data = request.get_json() or {}
    new_status = (data.get("status") or "").strip().capitalize()

    if new_status not in VALID_STATUSES:
        return jsonify({"status": "error", "message": f"Invalid status. Must be one of: {list(VALID_STATUSES)}"}), 400

    # Date and status business guards
    if new_status == "Completed" and trek.start_date > date.today():
        return jsonify({"status": "error", "message": "Cannot mark trek as completed before its start date"}), 400

    if new_status == "Open" and trek.end_date < date.today():
        return jsonify({"status": "error", "message": "Cannot open a trek whose end date has passed"}), 400

    # Cascade: auto-complete active bookings when trek completes
    if new_status == "Completed" and trek.status != "Completed":
        active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
        for b in active_bookings:
            b.status = "Completed"

    trek.status = new_status
    db.session.commit()
    invalidate_trek_cache()

    return jsonify({
        "status": "success",
        "message": f"Trek status updated to '{new_status}'",
        "data": trek.to_dict()
    }), 200


@treks_bp.route("/<int:trek_id>", methods=["DELETE"])
@admin_required
def delete_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    # Prevent deleting a trek that has active bookings
    active_booking = Booking.query.filter_by(trek_id=trek.id, status="Booked").first()
    if active_booking:
        return jsonify({
            "status": "error",
            "message": "Cannot delete trek with active confirmed bookings. Cancel bookings first or close the trek."
        }), 400

    db.session.delete(trek)
    db.session.commit()
    invalidate_trek_cache()

    return jsonify({
        "status": "success",
        "message": "Trek deleted successfully"
    }), 200
