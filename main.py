import asyncio
from typing import Any
from src.infra.core.logging import Log
from src.infra.repositories.timeline_extractor_repository import TimelineExtractorRepository
from src.data.interceptor_state import InterceptorState
from src.config.env import ConfigEnvs
from src.infra.factories.auction_extraction_current import auction_extraction_current_factory
from src.infra.repositories.get_auction_baches_repository import AuctionBatchesExtractorRepository
from argparse import ArgumentParser


global interceptorState

def interceptor_validator(values: dict[str, Any]) -> bool:
    if '/download' in values['url']:
        return False
    return True

interceptorState = InterceptorState.builder(validator=interceptor_validator)

async def main(extractor_key: str, headless: bool, months_before: int = 1, months_after: int = 1):
    url = ''
    if extractor_key == 'timeline':
        extractor_func = TimelineExtractorRepository(months_before=months_before, months_after=months_after)
        url = ConfigEnvs.TIMELINE_URL
    if extractor_key == 'batches':
        extractor_func = AuctionBatchesExtractorRepository()
        url = ConfigEnvs.SHOWCASE_URL

    scheduled_data_extraction = auction_extraction_current_factory(url, extractor_func=extractor_func, interceptor_state=interceptorState, headless=headless)
    await scheduled_data_extraction.run()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--headless', type=int, default=1, choices=[0, 1])
    parser.add_argument('--extractor', type=str, default='timeline', choices=['timeline', 'batches'])
    parser.add_argument('--months_before', type=int, default=1)
    parser.add_argument('--months_after', type=int, default=1)

    args = parser.parse_args()
    Log.info(f"Running with args: {args}")
    asyncio.run(main(
        extractor_key=args.extractor,
        headless=bool(args.headless),
        months_before=args.months_before,
        months_after=args.months_after
    ))
