from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Doc(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    status: Literal['STANDBY', 'IN-PROCESS', 'FAILED', 'DONE'] = 'STANDBY'
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
