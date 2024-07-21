from src.domain.use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase


class ScheduledDataExtraction:
    def __init__(self, data_extraction_service: GetAuctionBatchesUseCase):
        self.data_extraction_service = data_extraction_service

    async def run(self):
        result = await self.data_extraction_service.execute()
        return result