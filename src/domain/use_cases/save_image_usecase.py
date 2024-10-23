from typing import Callable

from pydantic import StrictStr
from src.data.hash_string import HashString
from src.domain.ports.file_downloader_repository import SaveFileRepository
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity


def extract_document_name(file_url: str) -> str:
    last_part_url = file_url.split("?")[-1]
    file_name = last_part_url.split("nome=")[-1]
    return f"{file_name}.pdf"


def extract_image_name(file_url: str) -> str:
    last_part_url = file_url.split("/")[-1]
    (file_name, extension) = last_part_url.split(".")
    return f"{file_name}.{extension.lower()}"


class SaveAuctionItemFilesUseCase:
    def __init__(
        self, file_repository: SaveFileRepository, hashing: HashString
    ) -> None:
        self._file_repository = file_repository
        self._hashing = hashing

    async def save(
        self, auction_item: AuctionItemEntity
    ) -> tuple[list[str], list[str]]:
        auction_folder_key = (
            f"{auction_item.city}-{auction_item.state}-{auction_item.period}"
        )
        auction_folder_hash = self._hashing(text=auction_folder_key)
        # TODO: Review this key
        auction_item_folder_key = f"{auction_item.city}-{auction_item.state}-{auction_item.period}-{auction_item.batch_number}-{auction_item.contract_number}"
        auction_item_folder_hash = self._hashing(text=auction_item_folder_key)
        images_urls = await self._download_list(
            urls=auction_item.images,
            folder=f"{auction_folder_hash}/{auction_item_folder_hash}/images",
            filename_extractor=extract_image_name,
        )

        docs_urls = await self._download_list(
            urls=auction_item.documents,
            folder=f"{auction_folder_hash}/{auction_item_folder_hash}/docs",
            filename_extractor=extract_document_name,
        )

        return (images_urls, docs_urls)

    async def _download_list(
        self, urls: list[str], folder: str, filename_extractor: Callable[[str], str]
    ) -> list[str]:
        urls_result: list[StrictStr] = []
        for img_url in urls:
            url = await self._file_repository.save(
                img_url, folder, extract_filename=filename_extractor
            )
            if url is not None and isinstance(url, str):
                urls_result.append(url)

        return urls_result
