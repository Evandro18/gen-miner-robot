from abc import abstractmethod
from io import BytesIO
import os
import re
from typing import Any, Optional, Union
import pypdf
import pymupdf
from pymupdf import Document

dirname = os.path.dirname(os.path.realpath(__file__))


class PDFTextExtractorAbstract:
    def _read_pdf(self, file: Union[BytesIO, str]) -> pypdf.PdfReader:
        try:
            readed = pypdf.PdfReader(file, strict=False)
            return readed
        except Exception as e:
            pass

        mu_document: Document = pymupdf.open(file)
        pdf_bytes = mu_document.tobytes(garbage=3, deflate=True)  # type: ignore
        bytes = BytesIO(pdf_bytes)
        return pypdf.PdfReader(bytes, strict=False)

    @abstractmethod
    def execute(self, file: Union[BytesIO, str]) -> dict[str, Any]:
        """Method to extract especific data from a pdf file"""
        raise NotImplementedError("Method not implemented")

    def _extract_text(self, file_reader: pypdf.PdfReader) -> str:
        full_text: str = ""
        for page in file_reader.pages:
            text = page.extract_text()
            full_text += text

        return full_text

    def _search_by_pattern(self, text: str, pattern: str) -> Optional[str]:
        result = re.search(pattern, text)
        if result:
            return result.group(1)
        return None
