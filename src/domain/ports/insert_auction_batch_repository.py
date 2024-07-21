from typing import Protocol

from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


class InsertAuctionBatchRepository(Protocol):
    async def execute(self, auction_item: list[AuctionItemEntity]) -> bool:
        raise NotImplementedError