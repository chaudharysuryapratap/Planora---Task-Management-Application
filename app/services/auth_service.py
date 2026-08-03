from datetime import datetime, timedelta
import uuid

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from jwt import ExpiredSignatureError
from passlib.hash import pbkdf2_sha256 as pwd_context

from app.database import db
from app.models.category import Category
from app.models.token import RefreshToken
from app.models.user import User


class AuthService:
    @staticmethod
    def register(user_data):
        existing_user = User.query.filter_by(email=user_data["email"]).first()
        if existing_user:
            return {"error": "Email already registered"}, 409

        user = User(
            id=str(uuid.uuid4()),
            name=user_data["name"],
            email=user_data["email"],
            password=pwd_context.hash(user_data["password"]),
        )

        db.session.add(user)
        db.session.flush()

        for name, color in (
            ("Work", "#FF6B6B"),
            ("Personal", "#4ECDC4"),
            ("Shopping", "#45B7D1"),
        ):
            db.session.add(
                Category(
                    id=str(uuid.uuid4()),
                    name=name,
                    color=color,
                    user_id=user.id,
                    is_default=True,
                )
            )

        access_token, refresh_token = AuthService._issue_tokens(user.id)
        db.session.commit()

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 201

    @staticmethod
    def login(credentials):
        user = User.query.filter_by(email=credentials["email"]).first()

        if not user or not pwd_context.verify(credentials["password"], user.password):
            return {"error": "Invalid credentials"}, 401

        access_token, refresh_token = AuthService._issue_tokens(user.id)
        db.session.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }, 200

    @staticmethod
    def _issue_tokens(user_id):
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(minutes=15),
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(days=7),
        )
        db.session.add(
            RefreshToken(
                id=str(uuid.uuid4()),
                token=refresh_token,
                user_id=user_id,
                expires_at=datetime.utcnow() + timedelta(days=7),
            )
        )
        return access_token, refresh_token

    @staticmethod
    def refresh_token(refresh_token):
        try:
            payload = decode_token(refresh_token)
        except ExpiredSignatureError:
            return {"error": "Refresh token expired"}, 401
        except Exception:
            return {"error": "Invalid refresh token"}, 401

        if payload.get("type") != "refresh":
            return {"error": "Invalid refresh token"}, 401

        token = RefreshToken.query.filter_by(token=refresh_token, revoked=False).first()
        if not token or token.expires_at <= datetime.utcnow():
            return {"error": "Invalid or expired refresh token"}, 401

        if str(payload.get("sub")) != token.user_id:
            return {"error": "Invalid refresh token"}, 401

        return {
            "access_token": create_access_token(
                identity=token.user_id,
                expires_delta=timedelta(minutes=15),
            )
        }, 200

    @staticmethod
    def logout(refresh_token):
        token = RefreshToken.query.filter_by(token=refresh_token).first()
        if token:
            token.revoked = True
            db.session.commit()

        return {"message": "Logged out successfully"}, 200
