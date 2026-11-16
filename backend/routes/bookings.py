from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.extensions import db, cache
from backend.models.booking import Booking
from backend.models.trek import Trek
from backend.utils.decorators import active_user_required, admin_required, staff_or_admin_required

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")

def invalidate_cache():
    try:
        cache.clear()
    except Exception:
        pass

@bookings_bp.route("", methods=["POST"])
@jwt_required()
@active_user_required
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    trek_id = data.get("trek_id")
    num_slots = data.get("num_slots", 1)

    if not trek_id or not isinstance(trek_id, int):
        return jsonify({"status": "error", "message": "Valid trek_id is required"}), 400

    if not isinstance(num_slots, int) or num_slots <= 0:
        return jsonify({"status": "error", "message": "num_slots must be a positive integer"}), 400

    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    # Trek must be open for booking
    if trek.status != "Open":
        return jsonify({"status": "error", "message": f"Trek is currently '{trek.status}' and not open for booking"}), 400

    # Cannot book a trek that has already started or passed
    if trek.start_date <= date.today():
        return jsonify({"status": "error", "message": "Cannot book a trek that has already started or passed"}), 400

    # Prevent duplicate active bookings by the same user
    existing_booking = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status="Booked").first()
    if existing_booking:
        return jsonify({
            "status": "error", 
            "message": "You already have an active booking for this trek. Cancel it first if you wish to re-book."
        }), 409

    # Check slot availability
    if trek.available_slots < num_slots:
        return jsonify({
            "status": "error",
            "message": f"Not enough slots available. Only {trek.available_slots} slots remaining."
        }), 400

    # Deduct slots atomically in database transaction
    trek.available_slots -= num_slots

    new_booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        num_slots=num_slots,
        status="Booked"
    )

    db.session.add(new_booking)
    db.session.commit()
    invalidate_cache()

    return jsonify({
        "status": "success",
        "message": "Trek booked successfully",
        "data": new_booking.to_dict()
    }), 201


@bookings_bp.route("/my-bookings", methods=["GET"])
@jwt_required()
@active_user_required
def get_my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    return jsonify({
        "status": "success",
        "data": [b.to_dict() for b in bookings]
    }), 200


@bookings_bp.route("/<int:booking_id>/cancel", methods=["POST"])
@jwt_required()
@active_user_required
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"status": "error", "message": "Booking not found"}), 404

    trek = booking.trek

    # Only booking owner, admin, or assigned staff can cancel
    is_owner = (booking.user_id == user_id)
    is_admin = (current_role == "admin")
    is_assigned_staff = (current_role == "staff" and trek.assigned_staff_id == user_id)

    if not (is_owner or is_admin or is_assigned_staff):
        return jsonify({"status": "error", "message": "You do not have permission to cancel this booking"}), 403

    if booking.status == "Cancelled":
        return jsonify({"status": "error", "message": "Booking is already cancelled"}), 400

    # Cannot cancel if trek has already started or passed
    if trek.start_date <= date.today():
        return jsonify({"status": "error", "message": "Cannot cancel booking for a trek that has already started or passed"}), 400

    # Rollback slots and update booking status
    booking.status = "Cancelled"
    trek.available_slots += booking.num_slots

    db.session.commit()
    invalidate_cache()

    return jsonify({
        "status": "success",
        "message": "Booking cancelled successfully and slots restored",
        "data": booking.to_dict()
    }), 200


@bookings_bp.route("/trek/<int:trek_id>", methods=["GET"])
@staff_or_admin_required
def get_trek_participants(trek_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"status": "error", "message": "Trek not found"}), 404

    # Staff can only view participants of their assigned treks
    if current_role == "staff" and trek.assigned_staff_id != current_user_id:
        return jsonify({"status": "error", "message": "You can only view participants for treks assigned to you"}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id, status="Booked").order_by(Booking.booking_date.asc()).all()

    return jsonify({
        "status": "success",
        "data": {
            "trek_id": trek.id,
            "trek_name": trek.name,
            "total_slots": trek.total_slots,
            "available_slots": trek.available_slots,
            "booked_slots": trek.total_slots - trek.available_slots,
            "participants": [b.to_dict() for b in bookings]
        }
    }), 200


@bookings_bp.route("", methods=["GET"])
@admin_required
def get_all_bookings():
    query = Booking.query

    status = request.args.get("status")
    if status in ["Booked", "Cancelled", "Completed"]:
        query = query.filter_by(status=status)

    trek_id = request.args.get("trek_id", type=int)
    if trek_id:
        query = query.filter_by(trek_id=trek_id)

    user_id = request.args.get("user_id", type=int)
    if user_id:
        query = query.filter_by(user_id=user_id)

    bookings = query.order_by(Booking.booking_date.desc()).all()

    return jsonify({
        "status": "success",
        "data": [b.to_dict() for b in bookings]
    }), 200
