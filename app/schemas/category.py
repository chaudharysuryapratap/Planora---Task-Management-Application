from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field("#808080", pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
