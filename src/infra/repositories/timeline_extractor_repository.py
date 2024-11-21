from typing import AsyncIterable, Optional
from pydantic import StrictStr
from src.domain.ports.extractors import ExtractorExtraParameters
from src.data.interceptor_state import InterceptorState
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity
from playwright.async_api import Page, ElementHandle
from urllib.parse import quote


file_url_base = (
    "https://servicebus2.caixa.gov.br/vitrinedejoias/api/cronograma/download?"
)


class TimelineExtractorRepository:

    async def __call__(
        self,
        page: Page,
        extra_params: ExtractorExtraParameters,
    ) -> AsyncIterable[AuctionItemEntity]:
        month_before_btn_selector = "#vitrineCronogramaFiltroMes #prev-1 a"
        await page.wait_for_selector(month_before_btn_selector)
        counter = 0
        while counter < extra_params.months_before:
            await page.click(month_before_btn_selector)
            await page.wait_for_selector(month_before_btn_selector)
            counter += 1

        counter = 0
        while counter < (extra_params.months_before + extra_params.months_after) + 1:
            if counter > 0:
                month_after_btn_selector = "#vitrineCronogramaFiltroMes #next-1 a"
                await page.click(month_after_btn_selector)
                await page.wait_for_selector(month_after_btn_selector)

            tr_selector = "#resultadoCronograma table tbody tr"
            table_rows = await page.query_selector_all(tr_selector)
            await page.wait_for_selector(tr_selector)
            for row in table_rows:
                table_cells = await row.query_selector_all("td")
                auction = {}
                for index, cell in enumerate(table_cells):
                    cell_text = await page.evaluate(
                        "(element) => element.textContent", cell
                    )
                    auction[f"cell_{index}"] = cell_text
                    if index == 6:
                        document_paths = await self._extract_documents_paths(page, cell)
                        auction["documents"] = document_paths
                    if index == 3:
                        auction["city"] = self._extract_city(cell_text)

                if len(auction.keys()) == 0:
                    continue

                yield AuctionItemEntity(
                    state=auction["cell_2"],
                    city=auction["city"],
                    period=auction["cell_0"],
                    exposure_period=auction["cell_1"],
                    withdrawal_period=auction["cell_4"],
                    documents=auction["documents"],
                    status=auction["cell_5"],
                    pick_up_location=auction["cell_3"],
                )

            counter += 1

    async def _extract_documents_paths(
        self, page: Page, cell: ElementHandle
    ) -> list[str]:
        options_selector = "select option"
        options = await cell.query_selector_all(options_selector)
        documents_path: list[StrictStr] = []
        for opt_index, option in enumerate(options):
            if opt_index == 0:
                continue
            option_file_value = await page.evaluate(
                "(element) => element.value", option
            )
            option_value = option_file_value.split("|")
            document_id = option_value[0]
            document_name = option_value[1]
            path = f"{file_url_base}documento={document_id}&nome={quote(document_name)}"
            if isinstance(path, str):
                documents_path.append(path)
        return documents_path

    def _extract_city(self, cell_text: str) -> str:
        city_state = cell_text.split("-")[-1]
        city = city_state.split("/")[0]
        return city
