import os
from datetime import date
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, decode_token
from backend.extensions import db, cache
from backend.models.booking import Booking
from backend.models.trek import Trek
from backend.models.export_job import ExportJob
from backend.models.user import User
from backend.tasks.export_tasks import export_user_bookings_csv
from backend.utils.decorators import active_user_required, admin_required, staff_or_admin_required

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")

VALID_BOOKING_STATUSES = {"Booked", "Cancelled", "Completed"}

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

    # Lock row to prevent race conditions during concurrent bookings
    trek = db.session.query(Trek).filter_by(id=trek_id).with_for_update().first()
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


@bookings_bp.route("", methods=["GET"])
@jwt_required()
@active_user_required
def get_bookings():
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    query = Booking.query

    # Status filter applies to all roles
    status = request.args.get("status")
    if status in ["Booked", "Cancelled", "Completed"]:
        query = query.filter_by(status=status)

    trek_id = request.args.get("trek_id", type=int)

    if current_role == "user":
        # Regular trekker can only see their own bookings
        query = query.filter_by(user_id=current_user_id)
        if trek_id:
            query = query.filter_by(trek_id=trek_id)

    elif current_role == "staff":
        # Staff can only see bookings for treks assigned to them
        query = query.join(Trek).filter(Trek.assigned_staff_id == current_user_id)
        if trek_id:
            query = query.filter(Booking.trek_id == trek_id)

    elif current_role == "admin":
        # Admin can view all bookings with optional filters
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


@bookings_bp.route("/<int:booking_id>", methods=["GET"])
@jwt_required()
@active_user_required
def get_booking(booking_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"status": "error", "message": "Booking not found"}), 404

    trek = booking.trek
    is_owner = (booking.user_id == current_user_id)
    is_admin = (current_role == "admin")
    is_assigned_staff = (current_role == "staff" and trek.assigned_staff_id == current_user_id)

    if not (is_owner or is_admin or is_assigned_staff):
        return jsonify({"status": "error", "message": "You do not have permission to view this booking"}), 403

    return jsonify({
        "status": "success",
        "data": booking.to_dict()
    }), 200


@bookings_bp.route("/<int:booking_id>", methods=["PUT"])
@staff_or_admin_required
def update_booking(booking_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"status": "error", "message": "Booking not found"}), 404

    trek = booking.trek

    # Staff can only edit bookings for treks assigned to them
    if current_role == "staff" and trek.assigned_staff_id != current_user_id:
        return jsonify({"status": "error", "message": "You can only modify bookings for treks assigned to you"}), 403

    data = request.get_json() or {}

    # Update status if provided
    if "status" in data:
        new_status = (data["status"] or "").strip().capitalize()
        if new_status not in VALID_BOOKING_STATUSES:
            return jsonify({
                "status": "error",
                "message": f"Invalid status. Must be one of: {list(VALID_BOOKING_STATUSES)}"
            }), 400

        if new_status != booking.status:
            # Cannot complete booking before trek has started
            if new_status == "Completed" and trek.start_date > date.today():
                return jsonify({"status": "error", "message": "Cannot mark booking as completed before trek start date"}), 400

            # Cannot cancel a booking that was already completed
            if booking.status == "Completed" and new_status == "Cancelled":
                return jsonify({"status": "error", "message": "Cannot cancel a booking that is already completed"}), 400

            was_active = booking.status in ["Booked", "Completed"]
            will_be_active = new_status in ["Booked", "Completed"]

            # Active -> Cancelled: restore slots
            if was_active and new_status == "Cancelled":
                trek.available_slots += booking.num_slots
            # Cancelled -> Active: re-check availability and deduct slots
            elif not was_active and will_be_active:
                if trek.start_date <= date.today():
                    return jsonify({"status": "error", "message": "Cannot reactivate booking for a trek that has started or passed"}), 400
                if trek.available_slots < booking.num_slots:
                    return jsonify({
                        "status": "error",
                        "message": f"Not enough slots available to reactivate. Only {trek.available_slots} remaining."
                    }), 400
                trek.available_slots -= booking.num_slots

            booking.status = new_status

    # Update num_slots if provided
    if "num_slots" in data:
        new_slots = data["num_slots"]
        if not isinstance(new_slots, int) or new_slots <= 0:
            return jsonify({"status": "error", "message": "num_slots must be a positive integer"}), 400

        if new_slots != booking.num_slots:
            diff = new_slots - booking.num_slots
            if booking.status in ["Booked", "Completed"]:
                if diff > 0 and trek.available_slots < diff:
                    return jsonify({
                        "status": "error",
                        "message": f"Not enough slots available. Only {trek.available_slots} slots remaining."
                    }), 400
                trek.available_slots -= diff
            booking.num_slots = new_slots

    db.session.commit()
    invalidate_cache()

    return jsonify({
        "status": "success",
        "message": "Booking updated successfully",
        "data": booking.to_dict()
    }), 200


@bookings_bp.route("/<int:booking_id>", methods=["DELETE"])
@admin_required
def delete_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"status": "error", "message": "Booking not found"}), 404

    trek = booking.trek
    # If booking was active, restore slots to inventory
    if booking.status == "Booked":
        trek.available_slots += booking.num_slots

    db.session.delete(booking)
    db.session.commit()
    invalidate_cache()

    return jsonify({
        "status": "success",
        "message": "Booking deleted successfully"
    }), 200


@bookings_bp.route("/export", methods=["POST"])
@jwt_required()
@active_user_required
def trigger_bookings_export():
    current_user_id = int(get_jwt_identity())
    job = ExportJob(user_id=current_user_id, status="PENDING")
    db.session.add(job)
    db.session.commit()

    # Dispatch Celery async task (with fallback if worker is offline)
    try:
        export_user_bookings_csv.delay(job.id)
    except Exception:
        export_user_bookings_csv(job.id)

    return jsonify({
        "status": "success",
        "message": "Export job initiated successfully",
        "data": job.to_dict()
    }), 202


@bookings_bp.route("/export-jobs", methods=["GET"])
@jwt_required()
@active_user_required
def list_export_jobs():
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_role = claims.get("role")

    query = ExportJob.query
    if current_role == "admin" and request.args.get("all") == "true":
        pass
    else:
        query = query.filter_by(user_id=current_user_id)

    jobs = query.order_by(ExportJob.created_at.desc()).all()
    return jsonify({
        "status": "success",
        "data": [job.to_dict() for job in jobs]
    }), 200


@bookings_bp.route("/export/<int:job_id>/download", methods=["GET"])
def download_exported_bookings(job_id):
    # Support token in Authorization header OR in query parameter (?token=...)
    token = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif request.args.get("token"):
        token = request.args.get("token").strip()

    if not token:
        return jsonify({"status": "error", "message": "Missing Authorization header or token query parameter"}), 401

    try:
        decoded = decode_token(token)
        current_user_id = int(decoded["sub"])
        current_role = decoded.get("role")
    except Exception:
        return jsonify({"status": "error", "message": "Invalid or expired token"}), 401

    user = db.session.get(User, current_user_id)
    if not user or user.status != "active":
        return jsonify({"status": "error", "message": "Account deactivated or not found"}), 403

    job = db.session.get(ExportJob, job_id)
    if not job:
        return jsonify({"status": "error", "message": "Export job not found"}), 404

    if job.user_id != current_user_id and current_role != "admin":
        return jsonify({"status": "error", "message": "Access denied"}), 403

    if job.status != "COMPLETED" or not job.file_path or not os.path.exists(job.file_path):
        return jsonify({
            "status": "error",
            "message": f"Export file not ready (current status: '{job.status}')"
        }), 400

    return send_file(
        job.file_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=os.path.basename(job.file_path)
    )
