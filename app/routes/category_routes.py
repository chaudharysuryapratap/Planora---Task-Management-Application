from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.middleware.auth_middleware import jwt_required
from app.schemas.category import CategoryCreateSchema, CategoryUpdateSchema
from app.services.category_service import CategoryService

bp = Blueprint("categories", __name__)


@bp.route("", methods=["GET"])
@jwt_required
def get_categories():
    result, status_code = CategoryService.get_categories(g.current_user.id)
    return jsonify(result), status_code


@bp.route("", methods=["POST"])
@jwt_required
def create_category():
    try:
        schema = CategoryCreateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = CategoryService.create_category(
            g.current_user.id,
            schema.model_dump(),
        )
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/<category_id>", methods=["PUT"])
@jwt_required
def update_category(category_id):
    try:
        schema = CategoryUpdateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = CategoryService.update_category(
            g.current_user.id,
            category_id,
            schema.model_dump(exclude_none=True),
        )
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/<category_id>", methods=["DELETE"])
@jwt_required
def delete_category(category_id):
    result, status_code = CategoryService.delete_category(
        g.current_user.id,
        category_id,
    )
    if status_code == 204:
        return "", 204
    return jsonify(result), status_code
