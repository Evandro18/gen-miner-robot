from src.domain.ports.search_auction_batches_repository import (
    SearchAuctionBatchesRepository,
)
from src.infra.repositories.pdf_document_result_extractor import (
    PDFDocumentResultExtractor,
)
from src.config.env import ConfigEnvs
from src.data.hash_string import HashString
from src.domain.use_cases.extract_auction_data_from_documents_use_case import (
    ExtractAuctionDataFromDocumentsUseCase,
)
from src.infra.repositories.pdf_document_extractor import PDFTextExtractor
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.file_downloader_repository import (
    FileDownloaderRepository,
    FileRepositoryConfig,
)
from src.infra.repositories.insert_auction_batch_repository import (
    InsertAuctionBatchRepository,
)
from src.domain.use_cases.process_auction_data_extraction_use_case import (
    ProcessAuctionDataExtractionUseCase,
)
from src.domain.use_cases.save_auction_batch_files_use_case import (
    SaveAuctionBatchFilesUseCase,
)

from src.infra.repositories.sqlserver.database import Base, Database
from src.infra.repositories.sqlserver.robot_execution_repository import (
    RobotExecutionRepository,
)


def auction_extraction_current_factory(
    extractors: dict[str, SearchAuctionBatchesRepository],
    robot_execution_repository: RobotExecutionRepository,
) -> ScheduledDataExtraction:

    file_repository_downloader = FileRepositoryConfig(
        folder_path=ConfigEnvs.IMAGES_FOLDER_PATH
    )
    save_images_usecase = SaveAuctionBatchFilesUseCase(
        file_repository=FileDownloaderRepository(config=file_repository_downloader),
        hashing=HashString(),
    )

    insert_auction_batch_repo = InsertAuctionBatchRepository()
    auction_batches_use_case = ProcessAuctionDataExtractionUseCase(
        auctions_repos=extractors,
        insert_auction_batch_repo=insert_auction_batch_repo,
        extract_auction_data_from_documents=ExtractAuctionDataFromDocumentsUseCase(
            document_extractor=PDFTextExtractor(),
            pdfdocument_result_extractor=PDFDocumentResultExtractor(),
        ),
        auction_item_docs_usecase=save_images_usecase,
        # robot_execution_repository=robot_execution_repository,
    )
    scheduled_data_extraction = ScheduledDataExtraction(
        data_extraction_service=auction_batches_use_case,
        robot_execution_repository=robot_execution_repository,
    )

    # Add gracefully shutfown to stop current process
    # GracefulKiller(auction_batches_use_case.kill_process)
    return scheduled_data_extraction
