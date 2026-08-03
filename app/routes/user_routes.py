from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.middleware.auth_middleware import jwt_required
from app.schemas.user import PasswordChangeSchema, UserUpdateSchema
from app.services.user_service import UserService

bp = Blueprint("users", __name__)


@bp.route("/me", methods=["GET"])
@jwt_required
def get_profile():
    return jsonify(g.current_user.to_dict()), 200


@bp.route("/me", methods=["PUT"])
@jwt_required
def update_profile():
    try:
        schema = UserUpdateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = UserService.update_profile(
            g.current_user.id,
            schema.model_dump(exclude_none=True),
        )
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/me/password", methods=["PUT"])
@jwt_required
def change_password():
    try:
        schema = PasswordChangeSchema(**(request.get_json(silent=True) or {}))
        result, status_code = UserService.change_password(
            g.current_user.id,
            schema.model_dump(),
        )
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422
