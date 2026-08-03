from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from passlib.hash import pbkdf2_sha256 as pwd_context
from pydantic import ValidationError

from app.database import db
from app.models.user import User
from app.schemas.user import UserCreateSchema
from app.services.auth_service import AuthService

frontend_bp = Blueprint("frontend", __name__)


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first", "warning")
            return redirect(url_for("frontend.login"))
        return function(*args, **kwargs)

    return decorated_function


@frontend_bp.route("/")
def index():
    return render_template("index.html")


@frontend_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not pwd_context.verify(password, user.password):
            flash("Invalid credentials", "danger")
            return render_template("login.html")

        auth_result, auth_status = AuthService.login({"email": email, "password": password})
        if auth_status != 200:
            flash("Login failed", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user.id
        session["user_email"] = user.email
        session["user_name"] = user.name
        session["access_token"] = auth_result["access_token"]
        session["refresh_token"] = auth_result["refresh_token"]

        flash("Login successful!", "success")
        return redirect(url_for("frontend.dashboard"))

    return render_template("login.html")


@frontend_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        try:
            schema = UserCreateSchema(
                name=(request.form.get("name") or "").strip(),
                email=(request.form.get("email") or "").strip().lower(),
                password=password,
            )
        except ValidationError as exc:
            first_error = exc.errors()[0].get("msg", "Invalid registration details")
            flash(first_error, "danger")
            return render_template("register.html")

        result, status = AuthService.register(schema.model_dump())
        if status != 201:
            flash(result.get("error", "Registration failed"), "danger")
            return render_template("register.html")

        user = result["user"]
        session.clear()
        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        session["user_name"] = user["name"]
        session["access_token"] = result["access_token"]
        session["refresh_token"] = result["refresh_token"]

        flash("Registration successful! You are now logged in.", "success")
        return redirect(url_for("frontend.dashboard"))

    return render_template("register.html")


@frontend_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@frontend_bp.route("/tasks")
@login_required
def tasks():
    return render_template("tasks.html")


@frontend_bp.route("/categories")
@login_required
def categories():
    return render_template("categories.html")


@frontend_bp.route("/profile")
@login_required
def profile():
    user = db.session.get(User, session.get("user_id"))
    if not user:
        session.clear()
        flash("Please log in again", "warning")
        return redirect(url_for("frontend.login"))
    return render_template("profile.html", user=user)


@frontend_bp.route("/logout", methods=["POST"])
def logout():
    refresh_token = session.get("refresh_token")
    if refresh_token:
        AuthService.logout(refresh_token)
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("frontend.index"))
