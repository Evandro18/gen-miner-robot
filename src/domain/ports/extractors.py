from typing import AsyncIterable, Callable, Optional
from openai import BaseModel
from playwright.async_api import Page
from pydantic import Field

from src.data.interceptor_state import InterceptorState
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


class ExtractorExtraParameters(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    months_before: int = Field(default=0)
    months_after: int = Field(default=0)
    request_interceptor_state: InterceptorState = Field(default=InterceptorState)
    headless: bool = Field(default=True)


ExtractorType = Callable[
    [Page, ExtractorExtraParameters], AsyncIterable[AuctionItemEntity]
]
