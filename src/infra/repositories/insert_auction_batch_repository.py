import json

import aiohttp

from src.config.env import ConfigEnvs
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity
from src.infra.core.logging import Log


class InsertAuctionBatchRepository:

    def __init__(self) -> None:
        self._path = f"{ConfigEnvs.AUCTIONS_API_URL}/auctions"

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
                        Log.info(f"Inserted {len(auction_item)} items")
                    return response.status == 200
            except Exception as e:
                Log.info(
                    f"Error on insert auction: {auction_item[0].auction_id} batch number: {auction_item[0].batch_number}, msg: {e}"
                )
                return False
