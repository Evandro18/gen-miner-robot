from datetime import datetime

from pydantic import BaseModel, Strict, StrictStr


class AuctionEntity(BaseModel):
    _id: StrictStr
    state: StrictStr
    city: StrictStr
    bid_value: float
    description: StrictStr
    batch_number: StrictStr
    contract_number: StrictStr
    centralizer: StrictStr
    bid_date: datetime
    result_date: datetime
    pick_up_location: StrictStr
    images: list[StrictStr]
    