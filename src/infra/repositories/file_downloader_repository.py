import os
from typing import Optional
from uuid import uuid4
import aiohttp
from pydantic import BaseModel, StrictStr

class ImageRepositoryConfig(BaseModel):
    folder_path: StrictStr

class FileDownloaderRepository:
    def __init__(self, config: ImageRepositoryConfig) -> None:
        self._folder_path = config.folder_path

    async def save(self, image_url: StrictStr, folder_hash: str) -> Optional[str]:
        self._check_or_create_folder(f'{self._folder_path}/{folder_hash}')

        path = None
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                image = await response.read()
                mime = response.headers.get('Content-Type')
                last_part_url = image_url.split('/')[-1]
                (file_name, extension) = last_part_url.split('.')
                
                if 'Indisponivel'.lower() in file_name.lower():
                    return None
                
                if mime is None:
                    print(f'Could not get mime type for image {image_url}')
                    return None

                image_name = f'{str(uuid4())}-{file_name}'
                path = f'{self._folder_path}/{folder_hash}/{image_name}.{extension.lower()}'
                with open(path, 'wb') as file:
                    file.write(image)
        return path
    
    def _check_or_create_folder(self, folder: str):
        if not os.path.exists(folder):
            os.makedirs(folder)
        