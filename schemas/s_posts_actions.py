from pydantic import (
    BaseModel, Field
)

from typing import (
    List
)
from uuid import UUID

class MemTakePollReq(BaseModel):
    poll_item_ids: List[UUID] 