from typing import Callable, Optional, Protocol
from pydantic import StrictStr


class SaveFileRepository(Protocol):
    async def save(self, file_url: StrictStr, folder_hash: str, extract_filename: Callable[[str], str]) -> Optional[str]:
        raise NotImplementedError