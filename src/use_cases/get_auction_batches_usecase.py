from datetime import date
from typing import Any, AsyncIterable, Protocol
from src.use_cases.entities.auction_entity import AuctionItemEntity
from src.use_cases.save_image_usecase import SaveAuctionItemImagesUseCase


class SearchAuctionBatchesRepository(Protocol):
    def execute(self) -> AsyncIterable[AuctionItemEntity]:
        raise NotImplementedError
    
class InsertAuctionBatchRepository(Protocol):
    async def execute(self, auction_item: list[AuctionItemEntity]) -> bool:
        raise NotImplementedError

class GetAuctionBatchesUseCase:
    def __init__(self,
            auction_repo: SearchAuctionBatchesRepository,
            auction_item_images_usecase: SaveAuctionItemImagesUseCase,
            insert_auction_batch_repo: InsertAuctionBatchRepository
        ):
        self._get_auction_data = auction_repo
        self._save_auction_images = auction_item_images_usecase
        self._insert_auction_batch = insert_auction_batch_repo

    async def execute(self) -> bool:
        try:
            items = []
            iterator = self._get_auction_data.execute()
            async for batch_item in iterator:
                batch_item.images = await self._save_auction_images.save(batch_item)
                items.append(batch_item)

                if len(items) == 10:
                    await self._insert_auction_batch.execute(items)
                    items.clear()
            return True
        except Exception as e:
            return False
    
    def _value_to_string(self, items: Any):
        if items is None:
            return ''
    
        if isinstance(items, date):
            return items.strftime('%Y-%m-%d')

        values = [str(item) for item in items if item is not None]
        if isinstance(values, list):
            return ", ".join(values)

        if ';' in str(values):
            values = str(values).replace(';', '.')
        return str(values)

    async def _write_csv_line(self, file, iterator: AsyncIterable[AuctionItemEntity]):
        is_first_item = True
        with open("auctions.csv", "w", encoding='utf-8') as file:
            async for batch_item in iterator:
                if is_first_item:
                    batch_keys = batch_item.model_dump().keys()
                    file.write("; ".join(batch_keys) + "\n")
                    is_first_item = False

                imgs = await self._save_auction_images.save(batch_item)
                batch_item.images = imgs
                values = [self._value_to_string(v) for v in batch_item.model_dump().values()]
                csv_row = ("; ".join(values) + '\n')
                file.write(csv_row)
        