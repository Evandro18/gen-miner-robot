from src.domain.ports.extractors import ExtractorExtraParameters
from src.domain.ports.search_auction_batches_repository import (
    SearchAuctionBatchesRepository,
)
from src.domain.use_cases.entities.auction_file_extracted_data import (
    AuctionDataExtracted,
)
from src.domain.use_cases.entities.data_extraction_type import DataExtractionType
from src.domain.use_cases.extract_auction_data_from_documents_use_case import (
    ExtractAuctionDataFromDocumentsUseCase,
)
from src.domain.use_cases.save_auction_batch_files_use_case import (
    SaveAuctionBatchFilesUseCase,
)
from src.infra.core.logging import Log
from src.infra.repositories.insert_auction_batch_repository import (
    InsertAuctionBatchRepository,
)


class ProcessAuctionDataExtractionUseCase:
    def __init__(
        self,
        auctions_repos: dict[str, SearchAuctionBatchesRepository],
        auction_item_docs_usecase: SaveAuctionBatchFilesUseCase,
        insert_auction_batch_repo: InsertAuctionBatchRepository,
        extract_auction_data_from_documents: ExtractAuctionDataFromDocumentsUseCase,
        # robot_execution_repository: RobotExecutionRepository,
    ):
        self._auction_extractors = auctions_repos
        self._save_auction_docs = auction_item_docs_usecase
        self._insert_auction_batch = insert_auction_batch_repo
        self._extract_auction_data_from_documents = extract_auction_data_from_documents
        # self._robot_execution_repository = robot_execution_repository

    async def execute(
        self, type: DataExtractionType, extra_params: ExtractorExtraParameters
    ) -> list[str]:
        try:
            Log.info(f"Starting data extraction for: {type.value}")
            failed_batches = []
            extractor = self._auction_extractors.get(type.value)
            if extractor is None:
                Log.error(f"Extractor not found for: {type.value}")
                return failed_batches

            result = extractor.execute(params=extra_params)
            iterator = aiter(result)
            while True:
                batch_item = await anext(iterator, None)

                if batch_item is None:
                    break
                # async for batch_item in iterator:
                imgs, docs = await self._save_auction_docs.save(batch_item)
                batch_item.images = imgs
                batch_item.documents = docs

                result = self._extract_auction_data_from_documents.execute(
                    batch_item.documents
                )

                # Here I need to extract this data, create an uuid for this item and save it with a flag to be executed again later.
                # In case of document data extraction error, then the batch id will not exists, so this batch will be ignored
                if result is None:
                    if batch_item.batch_number is not None:
                        Log.error(
                            f"Failed to extract data from documents: {batch_item}"
                        )
                        failed_batches.append(str(batch_item))
                    else:
                        Log.error(f"Any auction found for: {batch_item}")
                    continue

                extracted_data = AuctionDataExtracted(**result.model_dump())

                batch_item.auction_id = extracted_data.auction_id
                batch_item.result_date = extracted_data.result_date
                batch_item.sold_batches = extracted_data.sold_batches
                batch_item.unsold_batches = extracted_data.unsold_batches
                batch_item.exposure_period = extracted_data.exposure_date or ""

                Log.info(f"Extracted auction data from documents: {batch_item}")

                await self._insert_auction_batch.execute([batch_item])

            Log.info(f"Data extraction for: {type.value} finished")
            return failed_batches
        except Exception as e:
            Log.info(f"Error on ProcessAuctionDataExtractionUseCase: {e}")
            raise e
