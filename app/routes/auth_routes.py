from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.extensions import limiter
from app.middleware.auth_middleware import jwt_required as require_auth
from app.schemas.user import UserCreateSchema, UserLoginSchema
from app.services.auth_service import AuthService

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
@limiter.limit("5 per hour")
def register():
    try:
        schema = UserCreateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = AuthService.register(schema.model_dump())
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/login", methods=["POST"])
@limiter.limit("10 per 15 minutes")
def login():
    try:
        schema = UserLoginSchema(**(request.get_json(silent=True) or {}))
        result, status_code = AuthService.login(schema.model_dump())
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = (request.get_json(silent=True) or {}).get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 400

    result, status_code = AuthService.refresh_token(refresh_token)
    return jsonify(result), status_code


@bp.route("/logout", methods=["POST"])
def logout():
    refresh_token = (request.get_json(silent=True) or {}).get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 400

    result, status_code = AuthService.logout(refresh_token)
    return jsonify(result), status_code


@bp.route("/me", methods=["GET"])
@require_auth
def get_profile():
    from flask import g

    return jsonify(g.current_user.to_dict()), 200
