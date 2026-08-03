from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.middleware.auth_middleware import jwt_required
from app.schemas.task import TaskCreateSchema, TaskStatusUpdateSchema, TaskUpdateSchema
from app.services.task_service import TaskService

bp = Blueprint("tasks", __name__)


def _pagination_args():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return None

    if page < 1 or limit < 1 or limit > 100:
        return None
    return {"page": page, "limit": limit}


@bp.route("", methods=["GET"])
@jwt_required
def get_tasks():
    pagination = _pagination_args()
    if pagination is None:
        return jsonify({"error": "page must be >= 1 and limit must be between 1 and 100"}), 400

    filters = {
        key: value
        for key, value in {
            "status": request.args.get("status"),
            "priority": request.args.get("priority"),
            "category_id": request.args.get("category_id"),
        }.items()
        if value is not None
    }

    if filters.get("status") not in {None, "todo", "in_progress", "done", "archived"}:
        return jsonify({"error": "Invalid status filter"}), 400
    if filters.get("priority") not in {None, "low", "medium", "high"}:
        return jsonify({"error": "Invalid priority filter"}), 400

    result, status_code = TaskService.get_tasks(filters, pagination)
    return jsonify(result), status_code


@bp.route("", methods=["POST"])
@jwt_required
def create_task():
    try:
        schema = TaskCreateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = TaskService.create_task(schema.model_dump(exclude_none=True))
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/<task_id>", methods=["GET"])
@jwt_required
def get_task(task_id):
    result, status_code = TaskService.get_task(task_id)
    return jsonify(result), status_code


@bp.route("/<task_id>", methods=["PUT"])
@jwt_required
def update_task(task_id):
    try:
        schema = TaskUpdateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = TaskService.update_task(
            task_id,
            schema.model_dump(exclude_unset=True),
        )
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/<task_id>/status", methods=["PATCH"])
@jwt_required
def update_task_status(task_id):
    try:
        schema = TaskStatusUpdateSchema(**(request.get_json(silent=True) or {}))
        result, status_code = TaskService.update_status(task_id, schema.model_dump())
        return jsonify(result), status_code
    except ValidationError as exc:
        return jsonify({"error": "Validation failed", "details": exc.errors(include_context=False)}), 422


@bp.route("/<task_id>", methods=["DELETE"])
@jwt_required
def delete_task(task_id):
    result, status_code = TaskService.delete_task(task_id)
    if status_code == 204:
        return "", 204
    return jsonify(result), status_code


@bp.route("/search", methods=["GET"])
@jwt_required
def search_tasks():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query required"}), 400
    if len(query) > 255:
        return jsonify({"error": "Search query is too long"}), 400

    result, status_code = TaskService.search_tasks(query)
    return jsonify(result), status_code


@bp.route("/<task_id>/assign", methods=["POST"])
@jwt_required
def assign_task(task_id):
    assignee_id = (request.get_json(silent=True) or {}).get("user_id")
    if not assignee_id:
        return jsonify({"error": "User ID required"}), 400

    result, status_code = TaskService.assign_task(task_id, assignee_id)
    return jsonify(result), status_code
