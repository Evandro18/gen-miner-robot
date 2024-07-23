from typing import Any, AsyncIterable
from playwright.async_api import Page

from data.interceptor_state import InterceptorState

class ExtractorBase:
    
    async def execute(self, page: Page, interceptor_state: InterceptorState) ->  AsyncIterable[Any]:
        raise NotImplementedError