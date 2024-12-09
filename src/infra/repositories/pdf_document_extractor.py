import os
from io import BytesIO
from typing import Any, Optional, Union

from src.infra.core.logging import Log
from src.infra.repositories.pdf_reader_base import PDFTextExtractorAbstract

dirname = os.path.dirname(os.path.realpath(__file__))


class PDFTextExtractor(PDFTextExtractorAbstract):
    def execute(
        self, file: Union[BytesIO, str], **kwargs: Optional[Any]
    ) -> dict[str, Any]:
        try:
            file_reader = self._read_pdf(file)
            result = self._extract_text(file_reader)
            exposure_date = self._search_by_pattern(
                result,
                r"exposição\s{1,}dos\s{1,}lotes:\s{1,}de\s{1,}(\d{2}\/\d{2}\s{0,}\/\d{4}\s{1,}[aà]\s{1,}\d{2}\/\d{2}\/\d{4})",
            )
            props = {
                "auction_id": self._search_by_pattern(
                    result, r"Leilão\s{1,}nº\s{1,}(\d{1,}\/\d{1,}\/\d{1,}\.\d{1,})"
                ),
                "result_date": self._search_by_pattern(
                    result,
                    r"Relatório de Lances Empatado\s?s: dia (\d{2}\/\d{2}\/\d{4})",
                ),
                "exposure_date": (
                    exposure_date.replace(r" /", "/") if exposure_date else ""
                ),
            }
            return props
        except Exception as e:
            error_message = f"Error while extracting text from file - {e}"
            Log.error(error_message)
            raise ValueError(error_message)

    def _parse_exposure_date(self, date: str) -> str:
        if date is None:
            return ""
        return date.split("a")[0].strip()
