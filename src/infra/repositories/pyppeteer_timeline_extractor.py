from typing import AsyncIterable
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity
from pyppeteer.page import Page, ElementHandle
from urllib.parse import quote


url = 'https://vitrinedejoias.caixa.gov.br/Paginas/default.aspx'
file_url_base = 'https://servicebus2.caixa.gov.br/vitrinedejoias/api/cronograma/download?'


class TimelineExtractorPyppeteer:
    async def __call__(self, page: Page) -> AsyncIterable[AuctionItemEntity]:
        tr_selector = '#resultadoCronograma table tbody tr'
        table_rows = await page.querySelectorAll(tr_selector)
        await page.waitForSelector(tr_selector)
        for row in table_rows:
            table_cells = await row.querySelectorAll('td')
            auction = {}
            for index, cell in enumerate(table_cells):
                cell_text = await page.evaluate('(element) => element.textContent', cell)
                auction[f'cell_{index}'] = cell_text
                if index == 6:
                    document_paths = await self._extract_documents_paths(page, cell)
                    auction['documents'] = document_paths
                if index ==  3:
                    auction['cell_3'] = self._extract_city(cell_text)
            
            if len(auction.keys()) == 0:
                continue

            yield AuctionItemEntity(
                state=auction['cell_2'],
                city=auction['cell_3'],
                period=auction['cell_1'],
                documents=auction['documents']
            )

    async def _extract_documents_paths(self, page: Page, cell: ElementHandle) -> list[str]:
        options_selector = 'select option'
        options = await cell.querySelectorAll(options_selector)
        documents_path: list[str] = []
        for opt_index, option in enumerate(options):
            if opt_index == 0:
                continue
            option_file_value = await page.evaluate('(element) => element.value', option)
            option_value = option_file_value.split('|')
            document_id = option_value[0]
            document_name = option_value[1]
            path = f'{file_url_base}documento={document_id}&nome={quote(document_name)}'
            documents_path.append(path)
        return documents_path

    def _extract_city(self, cell_text: str) -> str:
        city_state = cell_text.split('-')[-1]
        city = city_state.split('/')[0]
        return city
