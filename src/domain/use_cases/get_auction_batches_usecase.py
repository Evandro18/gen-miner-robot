from datetime import date
from typing import Any, AsyncIterable
from src.domain.ports.search_auction_batches_repository import SearchAuctionBatchesRepository
from src.domain.use_cases.extract_data_from_documents import ExtractAuctionDataFromDocumentsUseCase
from src.domain.use_cases.save_image_usecase import SaveAuctionItemFilesUseCase
from src.infra.repositories.insert_auction_batch_repository import InsertAuctionBatchRepository
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


class GetAuctionBatchesUseCase:
    def __init__(self,
            auction_repo: SearchAuctionBatchesRepository,
            auction_item_docs_usecase: SaveAuctionItemFilesUseCase,
            insert_auction_batch_repo: InsertAuctionBatchRepository,
            extract_auction_data_from_documents: ExtractAuctionDataFromDocumentsUseCase
        ):
        self._get_auction_data = auction_repo
        self._save_auction_docs = auction_item_docs_usecase
        self._insert_auction_batch = insert_auction_batch_repo
        self._extract_auction_data_from_documents = extract_auction_data_from_documents

    async def execute(self) -> bool:
        try:
            items = []
            iterator = self._get_auction_data.execute()
            async for batch_item in iterator:
                imgs, docs = await self._save_auction_docs.save(batch_item)
                batch_item.images = imgs
                batch_item.documents = docs

                result = self._extract_auction_data_from_documents.execute(batch_item.documents)
                if result is None:
                    continue

                batch_item.auction_id = result.auction_id
                items.append(batch_item)

                # if len(items) == 1:
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

                imgs, docs = await self._save_auction_docs.save(batch_item)
                batch_item.images = imgs
                batch_item.documents = docs
                values = [self._value_to_string(v) for v in batch_item.model_dump().values()]
                csv_row = ("; ".join(values) + '\n')
                file.write(csv_row)
        