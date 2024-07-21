from io import BytesIO
import os
import re
from typing import Any, Optional, Union, cast
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextContainer, LTRect, LTPage
from pdfplumber.page import Page
from pdfplumber.table import Table
import pdfplumber
import pypdf
import pymupdf
from pymupdf import Document
from src.infra.core.logging import Log

dirname = os.path.dirname(os.path.realpath(__file__))
    

class PDFTextExtractor:
    def _read_pdf(self, file: Union[BytesIO, str]) -> pypdf.PdfReader:
        try:
            readed = pypdf.PdfReader(file, strict=False)
            return readed
        except Exception as e:
            pass
        
        mu_document: Document = pymupdf.open(file)
        pdf_bytes = mu_document.tobytes(garbage=3, deflate=True) # type: ignore
        bytes = BytesIO(pdf_bytes)
        return pypdf.PdfReader(bytes, strict=False)

    def execute(self, file: Union[BytesIO, str]) -> dict[str, Any]:
        try:
            file_reader = self._read_pdf(file)
            result = self._extract_text(file_reader)
            props = {
                'auction_id': self._search_by_pattern(result, r'Leilão\snº\s(\d{1,}\/\d{1,}\/\d{1,}\.\d{1,})'),
            }
            return props
        except Exception as e:
            error_message = f'Error while extracting text from file - {e}'
            Log.error(error_message)
            raise ValueError(error_message)
    
    def _extract_text(self, file_reader: pypdf.PdfReader) -> str:
        full_text: str = ''
        for page in file_reader.pages:
            text = page.extract_text()
            full_text += text

        return full_text
    
    def _search_by_pattern(self, text: str, pattern: str) -> Optional[str]:
        result = re.search(pattern, text)
        if result:
            return result.group(1)
        return None
