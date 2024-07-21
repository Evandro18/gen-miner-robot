from config.env import ConfigEnvs
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.file_downloader_repository import FileDownloaderRepository, FileRepositoryConfig
from src.infra.repositories.get_auction_baches_repository import PypeteerAuctionBatchesExtractor
from src.infra.repositories.insert_auction_batch_repository import InsertAuctionBatchRepository
from src.infra.repositories.pyppeteer_base import PypeteerExtractorBase
from use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase
from use_cases.save_image_usecase import SaveAuctionItemImagesUseCase


def auction_extraction_current_factory() -> ScheduledDataExtraction:
    url = ConfigEnvs.SHOWCASE_URL

    extactor_func = PypeteerAuctionBatchesExtractor()
    extractor_base = PypeteerExtractorBase(url, extactor_func)
    file_repository_downloader = FileRepositoryConfig(folder_path=ConfigEnvs.IMAGES_FOLDER_PATH)
    save_images_usecase = SaveAuctionItemImagesUseCase(
        file_repository=FileDownloaderRepository(config=file_repository_downloader)
    )
    insert_auction_batch_repo = InsertAuctionBatchRepository()
    auction_batches_use_case = GetAuctionBatchesUseCase(
        auction_repo=extractor_base,
        auction_item_images_usecase=save_images_usecase,
        insert_auction_batch_repo=insert_auction_batch_repo
    )
    scheduled_data_extraction = ScheduledDataExtraction(data_extraction_service=auction_batches_use_case)
    return scheduled_data_extraction