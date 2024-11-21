from typing import AsyncIterable, Protocol

from src.domain.ports.extractors import ExtractorExtraParameters
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


class SearchAuctionBatchesRepository(Protocol):
    def execute(
        self, params: ExtractorExtraParameters
    ) -> AsyncIterable[AuctionItemEntity]:
        raise NotImplementedError
