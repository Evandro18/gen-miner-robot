from pydantic import BaseModel


class BatchesWonByParticipant(BaseModel):
    document: str
    id: int
    batches: list[str]
