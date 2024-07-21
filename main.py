import asyncio
from src.data.hash_string import HashString
from src.domain.use_cases.extract_data_from_documents import ExtractAuctionDataFromDocumentsUseCase
from src.domain.use_cases.save_image_usecase import SaveAuctionItemFilesUseCase
from src.infra.repositories.pdf_document_extractor import PDFTextExtractor
from src.infra.repositories.pyppeteer_base import PypeteerExtractorBase
from src.infra.repositories.pyppeteer_timeline_extractor import TimelineExtractorPyppeteer
from src.config.env import ConfigEnvs
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.file_downloader_repository import FileDownloaderRepository, FileRepositoryConfig
from src.domain.use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase
# from src.domain.use_cases.save_image_usecase import SaveAuctionItemImagesUseCase
from src.infra.repositories.insert_auction_batch_repository import InsertAuctionBatchRepository


async def main():
    url = ConfigEnvs.TIMELINE_URL

    extactor_func = TimelineExtractorPyppeteer()
    extractor_base = PypeteerExtractorBase(url, extactor_func, headless=False)
    save_images_usecase = SaveAuctionItemFilesUseCase(
        file_repository=FileDownloaderRepository(config=FileRepositoryConfig(folder_path=ConfigEnvs.IMAGES_FOLDER_PATH)),
        hashing=HashString()
    )
    insert_auction_batch_repo = InsertAuctionBatchRepository()
    auction_batches_use_case = GetAuctionBatchesUseCase(
        auction_repo=extractor_base,
        auction_item_docs_usecase=save_images_usecase,
        insert_auction_batch_repo=insert_auction_batch_repo,
        extract_auction_data_from_documents=ExtractAuctionDataFromDocumentsUseCase(
            document_extractor=PDFTextExtractor()
        )
    )
    scheduled_data_extraction = ScheduledDataExtraction(data_extraction_service=auction_batches_use_case)
    await scheduled_data_extraction.run()

if __name__ == '__main__':
    asyncio.run(main())
