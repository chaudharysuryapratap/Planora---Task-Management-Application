from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.database import db
from app.models.user import User


def jwt_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user = db.session.get(User, get_jwt_identity())
            if not user:
                return jsonify({"error": "User not found"}), 401

            g.current_user = user
            return function(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401

    return decorated_function
