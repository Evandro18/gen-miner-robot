from io import BytesIO
from typing import Any, Protocol, Union


class DocumentExtractor(Protocol):
    def execute(self, file: Union[BytesIO, str]) -> dict[str, Any]:
        raise NotImplementedError