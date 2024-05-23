from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional, Any
from utilities.constants import ChoicesType
import datetime

class ChoicesBase(BaseModel):
    id: int

class MemberChoicesReq(BaseModel):
    type: int = Field(..., ge=ChoicesType.Interest_Area, le= ChoicesType.Language)
    lang_ia: List[int]

class LangIAResponse(BaseModel):
    id: int
    name: str
    create_date: datetime.date
    
class LangIACreate(BaseModel):
    name: str
    
class ChoicesCreate(BaseModel):
    type: int = Field(..., ge=ChoicesType.Interest_Area, le= ChoicesType.Language)  # Only allow values 0 or 1
    lang_ia: List[LangIACreate]