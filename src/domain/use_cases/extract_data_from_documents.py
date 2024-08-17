import re
from typing import Any, Optional
from src.infra.core.logging import Log
from src.domain.ports.document_extractor import DocumentExtractor
from src.domain.use_cases.entities.auction_file_extracted_data import (
    AuctionDataExtracted,
)


class ExtractAuctionDataFromDocumentsUseCase:
    def __init__(
        self,
        document_extractor: DocumentExtractor,
        pdfdocument_result_extractor: DocumentExtractor,
    ):
        self._document_extractor = document_extractor
        self._pdfdocument_result_extractor = pdfdocument_result_extractor

    def execute(self, document_paths: list[str]) -> Optional[AuctionDataExtracted]:
        Log.info("Extracting auction data from documents")
        try:
            document = self._extract_properties_from_notice(document_paths)
            extracted_data = self._extract_auction_result(document_paths)
            result = AuctionDataExtracted(
                **document,
                sold_batches=(
                    extracted_data["sold_batches"]
                    if "sold_batches" in extracted_data
                    else []
                ),
                unsold_batches=(
                    extracted_data["unsold_batches"]
                    if "unsold_batches" in extracted_data
                    else []
                ),
            )
            Log.info(f"Auction data extracted successfully id {result}")
            return result
        except Exception as e:
            Log.error(f"Error extracting auction data from documents: {e}")
            # TODO: Log error and enqueue this document to be processed later
            return None

    def _extract_properties_from_notice(
        self, document_paths: list[str]
    ) -> dict[str, str]:
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
            raise ValueError("Document path cannot be empty")

        document = self._document_extractor.execute(path)
        return document

    def _extract_auction_result(self, document_paths: list[str]) -> dict[str, Any]:
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
            return {}

        document = self._pdfdocument_result_extractor.execute(path)
        return document
