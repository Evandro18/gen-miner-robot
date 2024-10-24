from io import BytesIO
import os
from typing import Any, Union
from src.infra.repositories.pdf_reader_base import PDFTextExtractorAbstract
from src.infra.core.logging import Log

dirname = os.path.dirname(os.path.realpath(__file__))


class PDFTextExtractor(PDFTextExtractorAbstract):
    def execute(self, file: Union[BytesIO, str]) -> dict[str, Any]:
        try:
            file_reader = self._read_pdf(file)
            result = self._extract_text(file_reader)
            props = {
                "auction_id": self._search_by_pattern(
                    result, r"Leilão\s{1,}nº\s{1,}(\d{1,}\/\d{1,}\/\d{1,}\.\d{1,})"
                ),
                "result_date": self._search_by_pattern(
                    result, r"Relatório de Lances Empatados: dia (\d{2}\/\d{2}\/\d{4})"
                ),
                "exposure_date": self._search_by_pattern(
                    result,
                    r"exposição\s{1,}dos\s{1,}lotes:\s{1,}de\s{1,}(\d{2}\/\d{2}\/\d{4}\s{1,}a\s{1,}\d{2}\/\d{2}\/\d{4})",
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
