from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CreateParam(BaseModel):
    name: str
    synonyms: list[str]


class Param(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    synonyms: list[str]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
