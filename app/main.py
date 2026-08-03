from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.database import db, init_db
from app.extensions import jwt, limiter
from app.routes import auth_routes, category_routes, frontend_routes, task_routes, user_routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )
    init_db(app)
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(frontend_routes.frontend_bp)
    app.register_blueprint(auth_routes.bp, url_prefix="/api/v1/auth")
    app.register_blueprint(task_routes.bp, url_prefix="/api/v1/tasks")
    app.register_blueprint(user_routes.bp, url_prefix="/api/v1/users")
    app.register_blueprint(category_routes.bp, url_prefix="/api/v1/categories")

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(debug=False)
