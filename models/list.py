from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ListBase(BaseModel):
    name: str
    id_user: int

class ListDB(ListBase):
    id: int
    creation_date: Optional[datetime] = Field(default_factory=datetime.today)