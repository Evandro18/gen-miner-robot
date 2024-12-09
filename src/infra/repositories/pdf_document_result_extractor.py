import re
from io import BytesIO
from typing import Any, Optional, Union, cast

import pdfplumber
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pydantic import BaseModel

from src.domain.use_cases.entities.batches_won_by_document_entity import (
    BatchesWonByParticipant,
)
from src.infra.core.logging import Log


class AuctionParticipants(BaseModel):
    id: int
    document: str


class PDFDocumentResultExtractor:
    _possible_winners: list[str] = []

    _CPF_CNPJ_PATTERN = (
        r"^\d{3}\.\d{1}\w{2}\.\w{3}-\d{2}|\d{2}\.\d{1}\w{2}\.\w{3}\/\d{4}-\d{2}"
    )

    def __init__(self) -> None:
        self._table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "text",
            "snap_tolerance": 3,
            "edge_min_length": 5,
            "intersection_tolerance": 5,
        }

    def execute(
        self, file: Union[BytesIO, str], **kwargs: Any
    ) -> tuple[list[BatchesWonByParticipant], list[BatchesWonByParticipant]]:
        possible_winners = kwargs.get("participants", [])

        try:
            batches_by_document = self._extract_text_tables(file)
            auction_lot_won, auction_lot_not_won = self._flat_ids(
                possible_winners, batches_by_document
            )

            return auction_lot_won, auction_lot_not_won
        except Exception as e:
            error_message = f"Error while extracting text from file - {e}"
            Log.error(error_message)
            raise ValueError(error_message)

    def _flat_ids(
        self,
        possible_winners: list[AuctionParticipants],
        batches_by_document: dict[str, list[str]],
    ) -> tuple[list[BatchesWonByParticipant], list[BatchesWonByParticipant]]:
        auction_lot_won: list[BatchesWonByParticipant] = []
        auction_lot_not_won: list[BatchesWonByParticipant] = []
        for document in batches_by_document.keys():
            participant = next(
                (win for win in possible_winners if document in win.document), None
            )

            if participant:
                auction_lot_won.append(
                    BatchesWonByParticipant(
                        document=document,
                        id=participant.id,
                        batches=batches_by_document[document],
                    )
                )
                continue

            auction_lot_not_won.append(
                BatchesWonByParticipant(
                    document=document,
                    batches=batches_by_document[document],
                )
            )

        return auction_lot_won, auction_lot_not_won

    def _extract_text_tables(self, file_reader: Union[BytesIO, str]) -> Any:
        full_text = ""
        batches_by_document = {}
        current_document: Optional[str] = None
        add_batch = False
        self._pdf_plumber = pdfplumber.open(file_reader)
        for page in extract_pages(pdf_file=file_reader):
            page_component = [(element.y1, element) for element in page]
            page_component.sort(key=lambda x: x[0], reverse=True)
            elements = list(map(lambda component: component[1], page_component))

            page_text = self._extract_text_from_elements(
                elements=elements,
                batches_by_document=batches_by_document,
                current_document=current_document,
                add_batch=add_batch,
            )

            full_text += "".join(page_text)

        return batches_by_document

    def _extract_text_from_elements(
        self,
        elements: list[Any],
        batches_by_document: dict[str, list[str]],
        current_document: Optional[str],
        add_batch: bool,
    ) -> list[str]:
        page_text: list[str] = []
        text_container_extractor = PDFTextExtractorTextContainer()
        for element in elements:
            if text_container_extractor.match_kind(element=element):
                text = text_container_extractor.extract(
                    element=cast(LTTextContainer, element)
                )
                text = text.strip().replace(r"CPF/CNPJ: ", "")
                if re.search(self._CPF_CNPJ_PATTERN, text):
                    add_batch = True
                    current_document = text
                    batches_by_document[current_document] = []
                    continue

                if (
                    add_batch
                    and re.search(r"\d{4}\.\d{6}-\d{1,}", text)
                    and current_document is not None
                ):
                    batches_by_document[current_document].append(text)

        return page_text


class PDFTextExtractorTextContainer:

    def match_kind(self, element: Any) -> bool:
        return isinstance(element, LTTextContainer)

    def extract(self, element: LTTextContainer) -> str:
        text = element.get_text()
        return text
