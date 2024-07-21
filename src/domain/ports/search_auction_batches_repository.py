from typing import AsyncIterable, Protocol

from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


class SearchAuctionBatchesRepository(Protocol):
    def execute(self) -> AsyncIterable[AuctionItemEntity]:
        raise NotImplementedError