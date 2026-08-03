from datetime import datetime
import uuid

from app.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    tasks = db.relationship(
        "Task",
        foreign_keys="Task.user_id",
        back_populates="owner",
        lazy=True,
        cascade="all, delete-orphan",
    )
    assigned_tasks = db.relationship(
        "Task",
        foreign_keys="Task.assigned_to",
        back_populates="assignee",
        lazy=True,
    )
    categories = db.relationship(
        "Category",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan",
    )
    refresh_tokens = db.relationship(
        "RefreshToken",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
