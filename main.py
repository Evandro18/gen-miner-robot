import asyncio
from src.infra.commads.scheduled_data_extraction import ScheduledDataExtraction
from src.infra.repositories.get_auction_baches_repository import PypeteerExtractor
from src.use_cases.get_auction_batches_usecase import GetAuctionBatchesUseCase


async def main():
    url = 'https://vitrinedejoias.caixa.gov.br/Paginas/Busca.aspx'
    extractor = PypeteerExtractor(url)
    scheduled_data_extraction = ScheduledDataExtraction(GetAuctionBatchesUseCase(auction_repo=extractor))
    await scheduled_data_extraction.run()
    
if __name__ == '__main__':
    asyncio.run(main())