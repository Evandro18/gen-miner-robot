import aiohttp

from src.config.env import ConfigEnvs
from src.infra.core.logging import Log
from src.infra.repositories.pdf_document_result_extractor import AuctionParticipants


class GetAuctionParticipantsRepository:
    _path = f"{ConfigEnvs.AUCTIONS_API_URL}/auction-batch-winners/open"

    async def get_auction_participants(self) -> list[AuctionParticipants]:
        async with aiohttp.ClientSession() as session:

            headers = {"Content-Type": "application/json"}
            try:
                async with session.get(url=self._path, headers=headers) as response:
                    if not response.ok:
                        raise Exception(f"Error on get auction participants")
                    data = await response.json()
                    return [
                        AuctionParticipants(
                            document=self._parse_participant_document(item["document"]),
                            id=item["id"],
                        )
                        for item in data
                    ]
            except Exception as e:
                Log.info(f"Error on get auction participants, msg: {e}")
                raise e

    def _parse_participant_document(self, document: str) -> str:
        if len(document) == 11:
            return f"{document[:3]}.{document[3:4]}XX.XXX-{document[9:]}"
        if len(document) == 14:
            return (
                f"{document[:2]}.{document[2:3]}XX.XXX/{document[8:12]}-{document[12:]}"
            )

        raise ValueError("Invalid document")
