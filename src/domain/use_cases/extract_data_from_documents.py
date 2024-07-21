from typing import Optional
from src.infra.core.logging import Log
from src.domain.ports.document_extractor import DocumentExtractor
from src.domain.use_cases.entities.auction_file_extracted_data import AuctionDataExtracted



class ExtractAuctionDataFromDocumentsUseCase:
    def __init__(self, document_extractor: DocumentExtractor):
        self._document_extractor = document_extractor

    def execute(self, document_paths: list[str]) -> Optional[AuctionDataExtracted]:
        Log.info('Extracting auction data from documents')
        try:
            # Extracts the auction data from edital document
            path = next((path for path in document_paths if 'edital.pdf' == path.split('/')[-1].lower()), None)
            if not path:
                raise ValueError('Document path cannot be empty')

            document = self._document_extractor.execute(path)
            result = AuctionDataExtracted(**document)
            Log.info(f'Auction data extracted successfully id {result}')
            return result
        except Exception as e:
            Log.error(f'Error extracting auction data from documents: {e}')
            # TODO: Log error and enqueue this document to be processed later
            return None
