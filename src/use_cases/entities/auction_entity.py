from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, StrictStr


class AuctionItemEntity(BaseModel):
    state: StrictStr
    city: StrictStr
    period: StrictStr
    bid_value: Optional[float] = Field(default=None)
    description: StrictStr = Field(default=None)
    batch_number: StrictStr = Field(default=None)
    contract_number: StrictStr = Field(default=None)
    centralizer: StrictStr = Field(default=None)
    bid_date: Optional[StrictStr] = Field(default=None)
    result_date: Optional[date] = Field(default=None)
    pick_up_location: StrictStr = Field(default=None)
    images: list[StrictStr] = Field(default=[])
    price: Optional[float] = Field(default=None)
    