from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from utilities.constants import ChoicesType

class ChoicesBase(BaseModel):
    id: UUID

class LangIAResponse(ChoicesBase):
    name: str
    
class LangIACreate(BaseModel):
    name: str
    
class ChoicesCreate(BaseModel):
    type: int = Field(..., ge=ChoicesType.Interest_Area, le= ChoicesType.Language)  # Only allow values 0 or 1
    lang_ia: List[LangIACreate]