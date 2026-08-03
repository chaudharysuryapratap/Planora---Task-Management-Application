from datetime import datetime
import uuid

from app.database import db


class Task(db.Model):
    __tablename__ = "tasks"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('todo', 'in_progress', 'done', 'archived')",
            name="ck_tasks_status",
        ),
        db.CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority",
        ),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="todo", nullable=False)
    priority = db.Column(db.String(10), default="medium", nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id"), nullable=True)

    owner = db.relationship("User", foreign_keys=[user_id], back_populates="tasks")
    assignee = db.relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
            "assigned_to": self.assigned_to,
            "category_id": self.category_id,
        }
