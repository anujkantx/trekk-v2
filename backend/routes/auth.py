import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user import User
from backend.utils.decorators import active_user_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Public registration endpoint for Trekkers (general users).
    Admin and Staff accounts cannot be registered publicly.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "JSON body is required"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    contact_number = data.get("contact_number", "").strip() or None

    # Validations
    if not username:
        return jsonify({"error": "Bad Request", "message": "Username is required"}), 400
    if not email:
        return jsonify({"error": "Bad Request", "message": "Email is required"}), 400
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Bad Request", "message": "Invalid email address format"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Bad Request", "message": "Password must be at least 6 characters long"}), 400

    # Check for existing username or email
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Conflict", "message": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Conflict", "message": "Email already registered"}), 409

    # Strictly assign role='user' for public registration
    new_user = User(
        username=username,
        email=email,
        role="user",
        status="active",
        contact_number=contact_number
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": new_user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Unified login endpoint for all roles (Admin, Staff, Trekker).
    Returns a signed JWT access token containing role claims.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "JSON body is required"}), 400

    identifier = (data.get("username") or data.get("email") or "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "Bad Request", "message": "Username/Email and password are required"}), 400

    # Support login with either username or email
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Unauthorized", "message": "Invalid credentials"}), 401

    if user.status != "active":
        return jsonify({
            "error": "Forbidden", 
            "message": "Account has been suspended or blacklisted. Contact administrator."
        }), 403

    # Create JWT access token with role & identity claims
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "username": user.username,
            "status": user.status
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
@active_user_required
def get_profile():
    """
    Fetches the profile details of the currently authenticated user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Not Found", "message": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
@active_user_required
def update_profile():
    """
    Allows the authenticated user to update their contact number or change password.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Not Found", "message": "User not found"}), 404

    data = request.get_json() or {}

    # Update contact number
    if "contact_number" in data:
        user.contact_number = (data.get("contact_number") or "").strip() or None

    # Update password if requested
    if "new_password" in data:
        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")

        if not user.check_password(old_password):
            return jsonify({"error": "Unauthorized", "message": "Current password does not match"}), 401
        if len(new_password) < 6:
            return jsonify({"error": "Bad Request", "message": "New password must be at least 6 characters"}), 400

        user.set_password(new_password)

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": user.to_dict()
    }), 200
