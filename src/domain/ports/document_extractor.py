from io import BytesIO
from typing import Any, Optional, Protocol, Union


class DocumentExtractor(Protocol):
    def execute(
        self, file: Union[BytesIO, str], **kwargs: Optional[Any]
    ) -> dict[str, Any]:
        raise NotImplementedError
