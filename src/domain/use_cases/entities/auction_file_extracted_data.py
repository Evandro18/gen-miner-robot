from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from src.domain.use_cases.entities.batches_won_by_document_entity import (
    BatchesWonByParticipant,
)


class AuctionDataExtracted(BaseModel):
    auction_id: StrictStr
    result_date: Optional[StrictStr] = Field(default=None)
    exposure_date: Optional[StrictStr] = Field(default=None)
    sold_batches: list[BatchesWonByParticipant] = Field(default=[])
    unsold_batches: list[BatchesWonByParticipant] = Field(default=[])

    def __str__(self) -> StrictStr:
        return f"Auction ID: {self.auction_id}"
