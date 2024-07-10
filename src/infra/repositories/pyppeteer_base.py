import os
from typing import Any, AsyncIterable, Callable

PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

from pyppeteer import launch
from pyppeteer.page import Page


class PypeteerExtractorBase:
    def __init__(self, url: str, extractor_func: Callable[[Page], AsyncIterable[Any]], headless: bool = True):
        self._url = url
        self._headless = headless
        self._extractor_func = extractor_func
    
    async def __aenter__(self):
        self._browser = await launch({ 'headless': self._headless })
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._browser.close()
    
    async def execute(self) -> AsyncIterable[Any]:
        async with self:
            page = await self._browser.newPage()
            await page.goto(self._url, {
                'waitUntil': ['load', 'domcontentloaded', 'networkidle0', 'networkidle2']
            })
            async for batch in self._extractor_func(page):
                yield batch
