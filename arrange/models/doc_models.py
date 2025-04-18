from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Doc(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    created_at: date = Field(default_factory=datetime.now)
    updated_at: date = None
