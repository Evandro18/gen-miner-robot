import os
from typing import Callable, Optional
import aiohttp
from pydantic import BaseModel, StrictStr
from urllib.parse import unquote

from src.infra.core.logging import Log

class FileRepositoryConfig(BaseModel):
    folder_path: StrictStr

class FileDownloaderRepository:
    def __init__(self, config: FileRepositoryConfig) -> None:
        self._folder_path = config.folder_path
        self._calls = 0

    async def save(self, file_url: StrictStr, folder_hash: str, extract_filename: Callable[[str], str]) -> Optional[str]:
        self._calls += 1
        folder = f'{self._folder_path}/{folder_hash}'
        self._check_or_create_folder(folder)
        file_name = unquote(extract_filename(file_url))
        file_name = file_name.replace('/', '_')
        should_save = True
        should_request_again = False

        path = f'{folder}/{file_name}'
        async with aiohttp.ClientSession() as session:
            headers = {'cache-control': 'max-age=0'}
            async with session.get(file_url, headers=headers) as response:
                file_bytes = await response.read()
                mime = response.headers.get('Content-Type')

                if response.status != 200:
                    should_save = False
                    if self._calls < 3:
                        should_request_again = True
                    else:
                        Log.error(f'Error while downloading file {file_url} - {response.status}')

                if 'Indisponivel'.lower() in file_name.lower():
                    should_save = False
                
                if mime is None:
                    Log.error(f'Could not get mime type for file {file_url}')
                    should_save = False

                if mime is not None and 'application/json' in mime:
                    should_save = False
                
                if should_save:
                    with open(path, 'wb') as file:
                        file.write(file_bytes)

        if should_request_again:
            return await self.save(file_url, folder_hash, extract_filename)

        self._calls = 0
        if os.path.exists(f'{folder}/{file_name}'):
            return path
        return None
    
    def _check_or_create_folder(self, folder: str):
        if not os.path.exists(folder):
            os.makedirs(folder)
        