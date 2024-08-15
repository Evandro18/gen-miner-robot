import json
import aiohttp
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


class InsertAuctionBatchRepository:

    def __init__(self) -> None:
        self._path = "http://localhost:8082/backend-auctions/auctions"

    async def execute(self, auction_item: list[AuctionItemEntity]) -> bool:
        async with aiohttp.ClientSession() as session:

            payload = []
            for item in auction_item:
                payload_item = item.model_dump()

                payload.append(payload_item)

            payload_json = json.dumps(payload)
            headers = {"Content-Type": "application/json"}
            try:
                async with session.post(
                    url=self._path, data=payload_json, headers=headers
                ) as response:
                    if response.ok:
                        print(f"Inserted {len(auction_item)} items")
                    return response.status == 200
            except:
                return False
