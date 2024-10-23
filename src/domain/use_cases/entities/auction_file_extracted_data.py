from typing import Optional
from pydantic import BaseModel, Field, StrictStr


class AuctionDataExtracted(BaseModel):
    auction_id: StrictStr
    result_date: Optional[StrictStr] = Field(default=None)
    sold_batches: list[StrictStr]
    unsold_batches: list[StrictStr]

    def __str__(self) -> StrictStr:
        return f"Auction ID: {self.auction_id}"
