import asyncio
from typing import Any, AsyncIterable, Callable
from src.domain.ports.extractors import ExtractorExtraParameters, ExtractorType
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity
from src.infra.core.logging import Log
from src.data.interceptor_state import InterceptorState
from playwright.async_api import async_playwright, Page
from playwright.async_api import Request as PlaywrightRequest


class PlaywrightExtractorBase:
    def __init__(
        self,
        url: str,
        extractor_func: ExtractorType,
    ):
        self._url = url
        self._extractor_func = extractor_func

    async def execute(
        self, params: ExtractorExtraParameters
    ) -> AsyncIterable[AuctionItemEntity]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=params.headless)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            page.set_default_navigation_timeout(30000)

            async def handle_request(request: PlaywrightRequest) -> None:
                params.request_interceptor_state.set(
                    {"url": request.url, "method": request.method}
                )
                execute = params.request_interceptor_state.validate()
                if execute:
                    params.request_interceptor_state.clear()
                return

            page.on(
                "request",
                lambda request: asyncio.ensure_future(handle_request(request)),
            )
            await page.route(
                "**/*",
                lambda route: (
                    route.abort()
                    if "download" in route.request.url
                    else route.continue_()
                ),
            )

            await page.goto(self._url, wait_until="networkidle")
            async for batch in self._extractor_func(page, params):
                yield batch
