from pydantic import BaseModel, StrictStr


class AuctionDataExtracted(BaseModel):
    auction_id: StrictStr
    result_date: StrictStr
    
    def __str__(self) -> StrictStr:
        return f'Auction ID: {self.auction_id}'