import re # RegEx module
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user import User
from backend.utils.decorators import active_user_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    contact_number = data.get("contact_number", "").strip() or None

    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"status": "error", "message": "Invalid email address format"}), 400
    if not password or len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email already registered"}), 409

    # Public registration strictly defaults to 'user'
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
        "status": "success",
        "message": "User registered successfully",
        "data": new_user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body is required"}), 400

    identifier = (data.get("username") or data.get("email") or "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"status": "error", "message": "Username/Email and password are required"}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    if user.status != "active":
        return jsonify({
            "status": "error", 
            "message": "Account has been suspended or blacklisted by administrator"
        }), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "username": user.username,
            "status": user.status
        }
    )

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "user": user.to_dict()
        }
    }), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
@active_user_required
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    return jsonify({
        "status": "success",
        "data": user.to_dict()
    }), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
@active_user_required
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    data = request.get_json() or {}

    if "contact_number" in data:
        user.contact_number = (data.get("contact_number") or "").strip() or None

    if "new_password" in data:
        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")

        if not user.check_password(old_password):
            return jsonify({"status": "error", "message": "Current password does not match"}), 401
        if len(new_password) < 6:
            return jsonify({"status": "error", "message": "New password must be at least 6 characters"}), 400

        user.set_password(new_password)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Profile updated successfully",
        "data": user.to_dict()
    }), 200
