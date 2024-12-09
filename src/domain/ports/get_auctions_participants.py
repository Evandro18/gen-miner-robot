from typing import Protocol

from src.infra.repositories.pdf_document_result_extractor import AuctionParticipants


class GetAuctionParticipantsRepository(Protocol):

    async def get_auction_participants(self) -> list[AuctionParticipants]:
        raise NotImplementedError
