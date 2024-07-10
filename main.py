import asyncio
from infra.repositories.pyppeteer_base import PypeteerExtractorBase
from src.config.env import ConfigEnvs
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.get_auction_baches_repository import PypeteerAuctionBatchesExtractor
from infra.repositories.file_downloader_repository import FileDownloaderRepository, ImageRepositoryConfig
from src.use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase
from src.use_cases.save_image_usecase import SaveAuctionItemImagesUseCase
from src.infra.repositories.insert_auction_batch_repository import InsertAuctionBatchRepository


async def main():
    url = ConfigEnvs.SHOWCASE_URL

    extactor_func = PypeteerAuctionBatchesExtractor()
    extractor_base = PypeteerExtractorBase(url, extactor_func)
    save_images_usecase = SaveAuctionItemImagesUseCase(
        image_repository=FileDownloaderRepository(config=ImageRepositoryConfig(folder_path=ConfigEnvs.IMAGES_FOLDER_PATH))
    )
    insert_auction_batch_repo = InsertAuctionBatchRepository()
    auction_batches_use_case = GetAuctionBatchesUseCase(
        auction_repo=extractor_base,
        auction_item_images_usecase=save_images_usecase,
        insert_auction_batch_repo=insert_auction_batch_repo
    )
    scheduled_data_extraction = ScheduledDataExtraction(data_extraction_service=auction_batches_use_case)
    await scheduled_data_extraction.run()

if __name__ == '__main__':
    asyncio.run(main())