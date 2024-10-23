import asyncio
from typing import Any, AsyncIterable, Callable
from src.infra.core.logging import Log
from src.data.interceptor_state import InterceptorState
from playwright.async_api import async_playwright, Page
from playwright.async_api import Request as PlaywrightRequest

class PlaywrightExtractorBase:
    def __init__(self, url: str, extractor_func: Callable[[Page, InterceptorState], AsyncIterable[Any]], request_interceptor: InterceptorState, headless: bool = True):
        self._url = url
        self._headless = headless
        self._extractor_func = extractor_func
        self._request_interceptor = request_interceptor

    async def execute(self) -> AsyncIterable[Any]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self._headless)
            page = await browser.new_page()
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            page.set_default_navigation_timeout(30000)
            async def handle_request(request: PlaywrightRequest) -> None:
                self._request_interceptor.set({'url': request.url, 'method': request.method})
                execute = self._request_interceptor.validate()
                if execute:
                    self._request_interceptor.clear()
                return

            page.on('request', lambda request: asyncio.ensure_future(handle_request(request)))
            await page.route('**/*', lambda route: route.abort() if 'download' in route.request.url else route.continue_())

            await page.goto(self._url, wait_until='networkidle')
            async for batch in self._extractor_func(page, self._request_interceptor):
                yield batch

