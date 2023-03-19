from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class ActivityBase(BaseModel):
    name: str
    description: Optional[str] = None
    id_user: int
    id_list: int
    register_date: Optional[datetime] = Field(default_factory=datetime.today)
    
class ActivityDB(ActivityBase):
    id: int