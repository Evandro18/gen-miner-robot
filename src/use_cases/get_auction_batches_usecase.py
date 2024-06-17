from typing import AsyncIterable, Protocol


class SearchAuctionBatchesRepository(Protocol):
    def execute(self) -> AsyncIterable[dict[str, str]]:
        raise NotImplementedError

class GetAuctionBatchesUseCase:
    def __init__(self, auction_repo: SearchAuctionBatchesRepository):
        self.get_auction_data = auction_repo

    async def execute(self) -> bool:
        try:
            # items = []
            counter = 0
            iterator = self.get_auction_data.execute()
            with open("auctions.csv", "w", encoding='utf-8') as file:
                async for batch in iterator:
                    if counter == 0:
                        batch_keys = batch.keys()
                        file.write("; ".join(batch_keys) + "\n")
                        counter += 1
                    
                    values = [self._value_to_string(v) for v in batch.values()]
                    csv_row = ("; ".join(values) + '\n')
                    file.write(csv_row)
                    
            return True
        except Exception as e:
            return False
    
    def _value_to_string(self, value):
        if isinstance(value, list):
            return ", ".join(value)

        if ';' in str(value):
            value = str(value).replace(';', '.')
        return str(value)
        