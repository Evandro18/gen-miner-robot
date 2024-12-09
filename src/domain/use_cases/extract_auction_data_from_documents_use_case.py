import re
from typing import Optional

from src.domain.ports.document_extractor import DocumentExtractor
from src.domain.ports.get_auctions_participants import GetAuctionParticipantsRepository
from src.domain.use_cases.entities.auction_file_extracted_data import (
    AuctionDataExtracted,
)
from src.domain.use_cases.entities.batches_won_by_document_entity import (
    BatchesWonByParticipant,
)
from src.infra.core.logging import Log
from src.infra.repositories.pdf_document_result_extractor import (
    PDFDocumentResultExtractor,
)


class ExtractAuctionDataFromDocumentsUseCase:
    def __init__(
        self,
        document_extractor: DocumentExtractor,
        pdfdocument_result_extractor: PDFDocumentResultExtractor,
        get_auction_participants: GetAuctionParticipantsRepository,
    ):
        self._document_extractor = document_extractor
        self._pdfdocument_result_extractor = pdfdocument_result_extractor
        self._get_auction_participants = get_auction_participants

    async def execute(
        self, document_paths: list[str]
    ) -> Optional[AuctionDataExtracted]:
        Log.info("Extracting auction data from documents")
        try:
            document = self._extract_properties_from_notice(document_paths)
            auction_lot_won, auction_lot_not_won = await self._extract_auction_result(
                document_paths
            )
            if document is None:
                return None

            result = AuctionDataExtracted(
                **document,
                sold_batches=auction_lot_won,
                unsold_batches=auction_lot_not_won,
            )
            Log.info(f"Auction data extracted successfully id {result}")
            return result
        except Exception as e:
            Log.error(f"Error extracting auction data from documents: {e}")
            # TODO: Log error and enqueue this document to be processed later
            return None

    def _extract_properties_from_notice(
        self, document_paths: list[str]
    ) -> Optional[dict[str, str]]:
        # Extracts the auction data from edital document
        path = next(
            (
                path
                for path in document_paths
                if "edital.pdf" == path.split("/")[-1].lower()
            ),
            None,
        )
        if not path:
            Log.info("Document path cannot be empty")
            return None

        document = self._document_extractor.execute(path)
        return document

    async def _extract_auction_result(
        self, document_paths: list[str]
    ) -> tuple[list[BatchesWonByParticipant], list[BatchesWonByParticipant]]:
        # Extracts the auction data from ata document
        path = next(
            (
                path
                for path in document_paths
                if re.search(r"(resultado).*(cpf.*cnpj)", path.split("/")[-1].lower())
                is not None
            ),
            None,
        )
        if not path:
            Log.info("No auction result document found")
            return [], []

        participants = await self._get_auction_participants.get_auction_participants()
        auction_lot_won, auction_lot_not_won = (
            self._pdfdocument_result_extractor.execute(path, participants=participants)
        )
        return auction_lot_won, auction_lot_not_won
