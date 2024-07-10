import asyncio
import hashlib
from typing import Optional, Protocol, cast
from pydantic import StrictStr
from src.use_cases.entities.auction_entity import AuctionItemEntity


class SaveImageRepository(Protocol):
    async def save(self, image_url: StrictStr, folder_hash: str) -> Optional[str]:
        raise NotImplementedError

class SaveAuctionItemImagesUseCase:
    def __init__(self, image_repository: SaveImageRepository):
        self.image_repository = image_repository

    async def save(self, auction_item: AuctionItemEntity) -> list[str]:
        auction_folder_key = f'{auction_item.city}-{auction_item.state}-{auction_item.period}'
        auction_folder_hash = self._generate_folder_name_hash(text=auction_folder_key)
        
        auction_item_folder_key = f'{auction_item.city}-{auction_item.state}-{auction_item.period}-{auction_item.batch_number}-{auction_item.contract_number}'
        auction_item_folder_hash = self._generate_folder_name_hash(text=auction_item_folder_key)
        tasks: list[asyncio.Task] = []
        for img_url in auction_item.images:
            task = asyncio.create_task(self.image_repository.save(img_url, f'{auction_folder_hash}/{auction_item_folder_hash}'))
            tasks.append(task)

        result = await asyncio.gather(*tasks, return_exceptions=True)
        if isinstance(result, BaseException):
            raise result
        
        urls = cast(list[str], result)
        return urls
        

    def _generate_folder_name_hash(self, text: str) -> str:
        hash = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
        return f'{hash}'