from io import BytesIO
import re
from typing import Any, Union, cast
import pdfplumber
from src.infra.core.logging import Log
from src.infra.repositories.pdf_reader_base import PDFTextExtractorAbstract
from pdfminer.layout import LTChar, LTTextContainer, LTRect, LTPage
from pdfplumber.page import Page
from pdfplumber.table import Table
from typing import Any, Optional, Union
from pdfminer.high_level import extract_pages

class PDFDocumentResultExtractor(PDFTextExtractorAbstract):
    
    _CPF_CNPJ_PATTERN = r'^\d{3}\.\d{1}\w{2}\.\w{3}-\d{2}|\d{2}\.\d{1}\w{2}\.\w{3}\/\d{4}-\d{2}'
    
    def __init__(self) -> None:
        self._table_settings = { 'vertical_strategy': 'lines', 'horizontal_strategy': 'text', 'snap_tolerance': 3, 'edge_min_length': 5, 'intersection_tolerance': 5 }
    
    def execute(self, file: Union[BytesIO, str]) -> dict[str, Any]:
        try:
            # file_reader = self._read_pdf(file)
            batches_by_document = self._extract_text_tables(file)
            [k for k in batches_by_document.keys() if re.search(r'399.3XX.XXX-04', k)]
            unsold = self._flat_ids(batches_by_document)
            if '399.3XX.XXX-04' not in batches_by_document:
                return { 'sold_batches': [], 'unsold_batches': unsold }
            else:
                sold = batches_by_document['399.3XX.XXX-04']
                return { 'sold_batches': sold, 'unsold_batches': unsold }
        except Exception as e:
            error_message = f'Error while extracting text from file - {e}'
            Log.error(error_message)
            raise ValueError(error_message)
    
    def _flat_ids(self, batches_by_document: dict[str, list[str]]) -> list[str]:
        return [batch for batches in batches_by_document.values() for batch in batches]
    
    def _extract_text_tables(self, file_reader: Union[BytesIO, str]) -> Any:
        full_text = ''
        batches_by_document = {}
        current_document: Optional[str] = None
        add_batch = False
        self._pdf_plumber = pdfplumber.open(file_reader)
        for page_index, page in enumerate(extract_pages(pdf_file=file_reader)):
            page_component = [(element.y1, element) for element in page]
            page_component.sort(key=lambda x: x[0], reverse=True)
            elements = list(map(lambda component: component[1], page_component))

            page_text = self._extract_text_from_elements(
                elements=elements,
                batches_by_document=batches_by_document,
                current_document=current_document,
                add_batch=add_batch
            )

            full_text += ''.join(page_text)
        
        return batches_by_document

    def _extract_text_from_elements(self, elements: list[Any], batches_by_document: dict[str, list[str]], current_document: Optional[str], add_batch: bool) -> list[str]:
        page_text: list[str] = []
        text_container_extractor = PDFTextExtractorTextContainer()
        for i, element in enumerate(elements):
            if text_container_extractor.match_kind(element=element):
                text, line_formats = text_container_extractor.extract(element=cast(LTTextContainer, element))
                text = text.strip().replace(r'CPF/CNPJ: ', '')
                if re.search(self._CPF_CNPJ_PATTERN, text):
                    add_batch = True
                    current_document = text
                    batches_by_document[current_document] = []
                    continue

                if add_batch and re.search(r'\d{4}\.\d{6}-\d{1,}', text) and current_document is not None:
                    batches_by_document[current_document].append(text)

        return page_text


class PDFTextExtractorRectangle:
    
    def __init__(self, table_settings: dict[str, Any]) -> None:
        self._table_settings = table_settings
        self._table_num = 0
        self._is_text_inside_table = False
        self._is_first_element = True
        
    def match_kind(self, element: Any) -> bool:
        return isinstance(element, LTRect)
    
    def extract(self, element: LTRect, pumbler_page: Page, pdf_miner_page: LTPage) -> tuple[str, bool]:
        table_formatted_str: str = ''
        page_tables = pumbler_page.extract_tables(table_settings=self._table_settings)
        
        extracted = True
        if (len(page_tables) < 1):
            extracted = False
        else:
            table_str_raw = page_tables[self._table_num]
            table_formatted_str = self._table_to_string(table_str_raw)
        
        self._is_text_inside_table = True
        self._is_first_element = False
        
        tables = pumbler_page.find_tables(table_settings=self._table_settings)
        lower_side = self._get_page_lower_side(page=pumbler_page, table=tables[self._table_num]) if len(tables) > 0 else 0
        upper_side = element.y1
        
        table_already_extracted = (element.y0 >= lower_side and element.y1 <= upper_side)
        if not table_already_extracted and (self._table_num + 1) <= len(tables):
            self._table_num += 1
            self._is_text_inside_table = False
            self._is_first_element = True
        
        return (table_formatted_str, extracted)
    
    def _table_to_string(self, table: list[list[Optional[str]]]) -> str:
        table_string = ''
        for row_num in range(len(table)):
            row = table[row_num]
            cleaned_row = self._get_cleaned_row(row)
            if len(''.join(cleaned_row).strip()) == 0:
                continue
            table_string += f'| {" | ".join(cleaned_row)} |\n'
        
        return table_string
    
    def _get_cleaned_row(self, cells: list[Optional[str]]) -> list[str]:
        cleaned_cells: list[str] = []
        for cell in cells:
            if (cell is not None and '\n' in cell):
                cleaned_cells.append(cell.replace('\n', ''))
            elif cell is None:
                cleaned_cells.append('_')
            else:
                cleaned_cells.append(cell)

        return cleaned_cells

    def get_is_text_inside_table(self) -> bool:
        return self._is_text_inside_table
    
    def get_is_first_element(self) -> bool:
        return self._is_first_element
    
    def _get_page_lower_side(self, page: Page, table: Table) -> float:
        return page.bbox[3] - table.bbox[3]
    
    def _get_upper_side(self, element: LTRect) -> float:
        return element.y1
    
class PDFTextExtractorTextContainer:

    def match_kind(self, element: Any) -> bool:
        return isinstance(element, LTTextContainer)
    
    def extract(self, element: LTTextContainer) -> tuple[str, list[str]]:
        text = element.get_text()
        
        line_formats: list[Any] = []
        for text_line in element:
            if not isinstance(text_line, LTTextContainer):
                continue
            for character in text_line:
                if isinstance(character, LTChar):
                    line_formats.append(character.fontname)
                    line_formats.append(character.size)
        
        return (text, line_formats)