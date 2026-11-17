import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity
from backend.extensions import db, cache
from backend.models.user import User
from backend.models.trek import Trek
from backend.models.booking import Booking
from backend.utils.decorators import admin_required
from backend.tasks.report_tasks import generate_monthly_activity_report

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

def invalidate_cache():
    try:
        cache.clear()
    except Exception:
        pass

@admin_bp.route("/staff", methods=["POST"])
@admin_required
def create_staff():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")
    contact_number = (data.get("contact_number") or "").strip() or None

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Username, email, and password are required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"status": "error", "message": "Invalid email address format"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long"}), 400

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return jsonify({"status": "error", "message": "Username or email is already registered"}), 409

    new_staff = User(
        username=username,
        email=email,
        role="staff",
        status="active",
        contact_number=contact_number
    )
    new_staff.set_password(password)

    db.session.add(new_staff)
    db.session.commit()
    invalidate_cache()

    return jsonify({
        "status": "success",
        "message": "Staff member created successfully",
        "data": new_staff.to_dict()
    }), 201


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    query = User.query

    role = request.args.get("role", "").strip().lower()
    if role in ["user", "staff", "admin"]:
        query = query.filter_by(role=role)

    status = request.args.get("status", "").strip().lower()
    if status in ["active", "blocked"]:
        query = query.filter_by(status=status)

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    users = query.order_by(User.created_at.desc()).all()

    return jsonify({
        "status": "success",
        "data": [user.to_dict() for user in users]
    }), 200


@admin_bp.route("/users/<int:user_id>/status", methods=["PATCH"])
@admin_required
def toggle_user_status(user_id):
    current_admin_id = int(get_jwt_identity())

    # Prevent admin from deactivating or locking out their own account
    if user_id == current_admin_id:
        return jsonify({
            "status": "error",
            "message": "Administrators cannot deactivate or blacklist their own account"
        }), 400

    target_user = db.session.get(User, user_id)
    if not target_user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    data = request.get_json() or {}
    new_status = (data.get("status") or "").strip().lower()

    if new_status not in ["active", "blocked"]:
        return jsonify({
            "status": "error",
            "message": "Invalid status. Must be either 'active' or 'blocked'"
        }), 400

    target_user.status = new_status
    db.session.commit()
    invalidate_cache()

    return jsonify({
        "status": "success",
        "message": f"User '{target_user.username}' status updated to '{new_status}'",
        "data": target_user.to_dict()
    }), 200


@admin_bp.route("/dashboard-stats", methods=["GET"])
@admin_required
@cache.cached(timeout=60, key_prefix="admin_dashboard_stats")
def get_dashboard_stats():
    # User counts
    total_trekkers = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()

    # Trek metrics
    total_treks = Trek.query.count()
    open_treks = Trek.query.filter_by(status="Open").count()
    pending_treks = Trek.query.filter_by(status="Pending").count()
    completed_treks = Trek.query.filter_by(status="Completed").count()
    closed_treks = Trek.query.filter_by(status="Closed").count()

    # Booking metrics
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status="Booked").count()
    completed_bookings = Booking.query.filter_by(status="Completed").count()
    cancelled_bookings = Booking.query.filter_by(status="Cancelled").count()

    # Total platform revenue: sum of (num_slots * trek.price) for active/completed bookings
    revenue = db.session.query(
        db.func.sum(Booking.num_slots * Trek.price)
    ).join(Trek, Booking.trek_id == Trek.id).filter(
        Booking.status.in_(["Booked", "Completed"])
    ).scalar() or 0.0

    return jsonify({
        "status": "success",
        "data": {
            "users": {
                "total_trekkers": total_trekkers,
                "total_staff": total_staff,
                "total_registered": total_trekkers + total_staff
            },
            "treks": {
                "total": total_treks,
                "open": open_treks,
                "pending": pending_treks,
                "completed": completed_treks,
                "closed": closed_treks
            },
            "bookings": {
                "total": total_bookings,
                "booked": active_bookings,
                "completed": completed_bookings,
                "cancelled": cancelled_bookings
            },
            "financials": {
                "total_revenue": round(float(revenue), 2)
            }
        }
    }), 200


@admin_bp.route("/reports/monthly", methods=["GET"])
@admin_required
def download_monthly_report():
    res = generate_monthly_activity_report()
    if res.get("status") != "success":
        return jsonify({"status": "error", "message": res.get("message", "Failed to generate report")}), 500

    file_path = res["file_path"]
    filename = os.path.basename(file_path)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
