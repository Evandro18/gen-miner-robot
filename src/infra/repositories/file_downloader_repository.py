import asyncio
import os
from typing import Callable, Optional
from urllib.parse import unquote

import requests
from pydantic import BaseModel, StrictStr

from src.infra.core.logging import Log


class FileRepositoryConfig(BaseModel):
    folder_path: StrictStr


class FileDownloaderRepository:

    _calls_per_url: dict[str, int]
    _lock = False

    def __init__(self, config: FileRepositoryConfig) -> None:
        self._folder_path = config.folder_path
        self._calls_per_url = {}

    async def save(
        self,
        file_url: StrictStr,
        folder_hash: str,
        extract_filename: Callable[[str], str],
    ) -> Optional[str]:
        folder = f"{self._folder_path}/{folder_hash}"
        self._check_or_create_folder(folder)
        file_name = unquote(extract_filename(file_url))
        file_name = file_name.replace("/", "_")
        should_save = True
        should_request_again = False

        path = f"{folder}/{file_name}"

        if os.path.exists(f"{folder}/{file_name}"):
            return path

        url_not_in_dict = file_url not in self._calls_per_url
        self._calls_per_url[file_url] = (
            0 if url_not_in_dict else self._calls_per_url[file_url] + 1
        )

        headers = {"cache-control": "max-age=0"}
        response = requests.get(file_url, headers=headers)
        file_bytes = response.content
        mime = response.headers.get("Content-Type")

        if response.status_code != 200:
            Log.error(
                f"Failed to download file trying again {file_url} - {response.status_code}"
            )
            should_save = False
            time_to_wait = 5
            current_loop = self._calls_per_url[file_url]
            if current_loop < 3:
                should_request_again = True
                Log.info(f"Waiting 5 seconds to try again {file_url}")
                await asyncio.sleep(time_to_wait * (1 + (current_loop / 10)))
            else:
                Log.error(
                    f"Error while downloading file {file_url} - {response.status_code}"
                )

            if "Indisponivel".lower() in file_name.lower():
                should_save = False

            if mime is None:
                Log.error(f"Could not get mime type for file {file_url}")
                should_save = False

            if mime is not None and "application/json" in mime:
                should_save = False

        if should_save:
            with open(path, "wb") as file:
                file.write(file_bytes)

        if should_request_again:
            recursive_result = await self.save(file_url, folder_hash, extract_filename)
            return recursive_result

        del self._calls_per_url[file_url]
        return path if should_save else None

    def _check_or_create_folder(self, folder: str):
        if not os.path.exists(folder):
            os.makedirs(folder)
