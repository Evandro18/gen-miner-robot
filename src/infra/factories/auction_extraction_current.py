from typing import Any, AsyncIterable, Callable
from src.data.interceptor_state import InterceptorState
from src.config.env import ConfigEnvs
from src.data.hash_string import HashString
from src.domain.use_cases.extract_data_from_documents import ExtractAuctionDataFromDocumentsUseCase
from src.infra.repositories.pdf_document_extractor import PDFTextExtractor
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.file_downloader_repository import FileDownloaderRepository, FileRepositoryConfig
from src.infra.repositories.insert_auction_batch_repository import InsertAuctionBatchRepository
from src.infra.repositories.extractor_base import PypeteerExtractorBase
from src.domain.use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase
from src.domain.use_cases.save_image_usecase import SaveAuctionItemFilesUseCase
from playwright.async_api import Page


def auction_extraction_current_factory(url: str, extractor_func: Callable[[Page, InterceptorState], AsyncIterable[Any]], interceptor_state: InterceptorState, headless = True) -> ScheduledDataExtraction:
    extractor_base = PypeteerExtractorBase(url, extractor_func, request_interceptor=interceptor_state, headless=headless)
    file_repository_downloader = FileRepositoryConfig(folder_path=ConfigEnvs.IMAGES_FOLDER_PATH)
    save_images_usecase = SaveAuctionItemFilesUseCase(
        file_repository=FileDownloaderRepository(config=file_repository_downloader),
        hashing=HashString()
    )

    insert_auction_batch_repo = InsertAuctionBatchRepository()
    auction_batches_use_case = GetAuctionBatchesUseCase(
        auction_repo=extractor_base,
        insert_auction_batch_repo=insert_auction_batch_repo,
        extract_auction_data_from_documents=ExtractAuctionDataFromDocumentsUseCase(
            document_extractor=PDFTextExtractor()
        ),
        auction_item_docs_usecase=save_images_usecase
    )
    scheduled_data_extraction = ScheduledDataExtraction(data_extraction_service=auction_batches_use_case)
    return scheduled_data_extraction