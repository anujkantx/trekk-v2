from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.models.user import User

def role_required(*allowed_roles):
    """
    Decorator to restrict endpoint access based on JWT role claim.
    Allowed roles: 'admin', 'staff', 'user'
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT exists and is valid
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Access restricted. Required roles: {list(allowed_roles)}. Your role: '{user_role}'"
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_required():
    """Restricts access exclusively to System Administrators."""
    return role_required("admin")

def staff_required():
    """Restricts access exclusively to Trek Staff."""
    return role_required("staff")

def staff_or_admin_required():
    """Allows access to both Trek Staff and Admin."""
    return role_required("staff", "admin")

def active_user_required(fn):
    """
    Decorator to ensure the authenticated user account is active (not blacklisted/suspended).
    Checks real-time status in the database to catch mid-session blacklisting.
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Unauthorized", "message": "User not found"}), 401

        if user.status != "active":
            return jsonify({
                "error": "Forbidden",
                "message": "Your account has been deactivated or blacklisted by the administrator."
            }), 403

        return fn(*args, **kwargs)
    return decorator
