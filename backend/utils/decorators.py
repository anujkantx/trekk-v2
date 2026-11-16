from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.extensions import db
from backend.models.user import User

def role_required(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 401

            # Check DB status to catch mid-session blacklisting
            if user.status != "active":
                return jsonify({
                    "status": "error",
                    "message": "Account has been deactivated or blacklisted by administrator"
                }), 403

            if user.role not in allowed_roles:
                return jsonify({
                    "status": "error",
                    "message": f"Access restricted. Required roles: {list(allowed_roles)}"
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_required(fn=None):
    decorator = role_required("admin")
    return decorator(fn) if fn else decorator

def staff_required(fn=None):
    decorator = role_required("staff")
    return decorator(fn) if fn else decorator

def staff_or_admin_required(fn=None):
    decorator = role_required("staff", "admin")
    return decorator(fn) if fn else decorator

def active_user_required(fn=None):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 401

            # Check DB status to catch mid-session blacklisting
            if user.status != "active":
                return jsonify({
                    "status": "error",
                    "message": "Account has been deactivated or blacklisted by administrator"
                }), 403

            return func(*args, **kwargs)
        return decorator
    return wrapper(fn) if fn else wrapper
