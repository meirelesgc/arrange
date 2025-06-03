from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CreatePatient(BaseModel):
    full_name: str
    date_of_birth: Optional[date]
    gender: Optional[Literal['MALE', 'FEMALE']]
    phone: Optional[str]
    email: Optional[str]


class Patient(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    full_name: str
    date_of_birth: Optional[date]
    gender: Optional[Literal['MALE', 'FEMALE']]
    phone: Optional[str]
    email: Optional[str]

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
