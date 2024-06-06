from pydantic import (
    BaseModel, Field
)

from typing import (
    List
)

class MemTakePollReq(BaseModel):
    poll_item_ids: List[str] 