from collections.abc import AsyncIterable
from typing import Callable


class GetAuctionBatchesUseCase:
    def __init__(self, auction_repo: Callable[[], AsyncIterable[dict[str, str]]]):
        self.get_auction_data = auction_repo

    async def execute(self) -> bool:
        try:
            items = []
            iterator = self.get_auction_data()
            async for batch in iterator:
                items.append(batch)
                if len(items) == 10:
                    # save items
                    items = []
            return True
        except Exception as e:
            return False
        