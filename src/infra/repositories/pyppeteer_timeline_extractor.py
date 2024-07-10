import asyncio
from typing import Any, AsyncIterable
from pyppeteer_base import PypeteerExtractorBase
from pyppeteer.page import Page

url = 'https://vitrinedejoias.caixa.gov.br/Paginas/default.aspx'
file_url_base = 'https://servicebus2.caixa.gov.br/vitrinedejoias/api/cronograma/download?'

async def timeline_extractor_pyppeteer(page: Page) -> AsyncIterable[Any]:
    tr_selector = '#resultadoCronograma table tbody tr'
    # await page.waitFor(1000)
    table_rows = await page.querySelectorAll(tr_selector)
    await page.waitForSelector(tr_selector)
    auctions: list[dict[str, str]] = []
    for row_index, row in enumerate(table_rows):
        table_cells = await row.querySelectorAll('td')
        auction = {}
        for index, cell in enumerate(table_cells):
            cell_text = await page.evaluate('(element) => element.textContent', cell)
            auction[f'cell_{index}'] = cell_text
            if index == 6:
                options_selector = 'select option'
                options = await cell.querySelectorAll(options_selector)
                for opt_index, option in enumerate(options):
                    if opt_index == 0:
                        continue
                    option_file_value = await page.evaluate('(element) => element.value', option)
                    option_value = option_file_value.split('|')
                    document_id = option_value[0]
                    document_name = option_value[1]
                    path = f'{file_url_base}documento={document_id}&nome={document_name}'
                    auction[f'option_{opt_index}'] = path
        yield auction

extractor = PypeteerExtractorBase(url=url, extractor_func=timeline_extractor_pyppeteer, headless=False)
extractor.execute()

async def main():
    iterator = extractor.execute()
    async for auction in iterator:
        print(auction)
if __name__ == '__main__':
    asyncio.run(main())