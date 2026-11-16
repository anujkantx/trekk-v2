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

@treks_bp.route("", methods=["GET"])
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

    # Status visibility based on role
    current_role = None
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims:
            current_role = claims.get("role")
    except Exception:
        pass

    requested_status = request.args.get("status", "").strip().capitalize()
    if requested_status in VALID_STATUSES:
        if current_role in ["admin", "staff"]:
            query = query.filter_by(status=requested_status)
        elif requested_status in ["Approved", "Open"]:
            query = query.filter_by(status=requested_status)
    elif current_role not in ["admin", "staff"]:
        # Public users only see open and approved treks
        query = query.filter(Trek.status.in_(["Approved", "Open"]))

    treks = query.order_by(Trek.start_date.asc()).all()

    return jsonify({
        "status": "success",
        "data": [trek.to_dict() for trek in treks]
    }), 200


@treks_bp.route("/<int:trek_id>", methods=["GET"])
def get_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    # If trek is Open or Approved, it is publicly visible
    if trek.status in ["Open", "Approved"]:
        return jsonify({
            "status": "success",
            "data": trek.to_dict()
        }), 200

    # For non-public statuses (Pending, Closed, Completed), verify permissions
    current_role = None
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims:
            current_role = claims.get("role")
            current_user_id = int(get_jwt_identity())
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
        staff_user = User.query.get(assigned_staff_id)
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
    trek = Trek.query.get(trek_id)
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
            staff_user = User.query.get(staff_id)
            if not staff_user or staff_user.role != "staff":
                return jsonify({"status": "error", "message": "Assigned user must have 'staff' role"}), 400
            trek.assigned_staff_id = staff_id
        else:
            trek.assigned_staff_id = None

    # Apply validated changes (including status and dates safely)
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
    trek = Trek.query.get(trek_id)
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
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    # Prevent deleting a trek that has active bookings
    active_booking = Booking.query.filter_by(trek_id=trek.id, status="confirmed").first()
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
