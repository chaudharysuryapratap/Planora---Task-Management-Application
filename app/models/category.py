from datetime import datetime
import uuid

from app.database import db


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default="#808080", nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    tasks = db.relationship("Task", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "is_default": self.is_default,
            "user_id": self.user_id,
            "tasks_count": len([task for task in self.tasks if task.deleted_at is None]),
        }
