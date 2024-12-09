from typing import Optional

from pydantic import BaseModel, Field


class BatchesWonByParticipant(BaseModel):
    document: str
    id: Optional[int] = Field(default=None)
    batches: list[str]
