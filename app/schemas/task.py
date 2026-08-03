from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field, field_validator


class TaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field("medium", pattern=r"^(low|medium|high)$")
    due_date: Optional[datetime] = None
    category_id: Optional[str] = None

    @field_validator("category_id")
    @classmethod
    def validate_uuid(cls, value):
        if value:
            try:
                uuid.UUID(value)
            except ValueError as exc:
                raise ValueError("Invalid category ID format") from exc
        return value


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high)$")
    due_date: Optional[datetime] = None
    category_id: Optional[str] = None

    @field_validator("title", "priority")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @field_validator("category_id")
    @classmethod
    def validate_uuid(cls, value):
        if value:
            try:
                uuid.UUID(value)
            except ValueError as exc:
                raise ValueError("Invalid category ID format") from exc
        return value


class TaskStatusUpdateSchema(BaseModel):
    status: str = Field(..., pattern=r"^(todo|in_progress|done|archived)$")
