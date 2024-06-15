import asyncio
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.get_auction_baches_repository import search_auction_batches
from src.use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase


async def main():
    scheduled_data_extraction = ScheduledDataExtraction(GetAuctionBatchesUseCase(auction_repo=search_auction_batches))
    await scheduled_data_extraction.run()
    
if __name__ == '__main__':
    asyncio.run(main())