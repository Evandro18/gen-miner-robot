import asyncio
import threading
from argparse import ArgumentParser
from time import localtime, sleep, strftime, time
from typing import Any

import schedule

from src.config.env import ConfigEnvs
from src.data.interceptor_state import InterceptorState
from src.domain.ports.extractors import ExtractorExtraParameters
from src.infra.commads.scheduled_data_extraction import DataExtractionType
from src.infra.core.logging import Log
from src.infra.factories.auction_extraction_current import (
    auction_extraction_current_factory,
)
from src.infra.repositories.extractor_base import PlaywrightExtractorBase
from src.infra.repositories.get_auction_baches_repository import (
    AuctionBatchesExtractorRepository,
)
from src.infra.repositories.sqlserver.database import Database
from src.infra.repositories.sqlserver.robot_execution_repository import (
    RobotExecutionRepository,
)
from src.infra.repositories.timeline_extractor_repository import (
    TimelineExtractorRepository,
)

global interceptorState


def interceptor_validator(values: dict[str, Any]) -> bool:
    if "/download" in values["url"]:
        return False
    return True


interceptor_state = InterceptorState.builder(validator=interceptor_validator)

extractor_timeline_strategy = PlaywrightExtractorBase(
    ConfigEnvs.TIMELINE_URL, TimelineExtractorRepository()
)

extractor_batches_strategy = PlaywrightExtractorBase(
    ConfigEnvs.SHOWCASE_URL, AuctionBatchesExtractorRepository()
)

scheduled_data_extraction = auction_extraction_current_factory(
    extractors={
        DataExtractionType.TIMELINE: extractor_timeline_strategy,
        DataExtractionType.BATCHES.value: extractor_batches_strategy,
    },
    robot_execution_repository=RobotExecutionRepository(Database()),
)


async def job(
    extractor_key: DataExtractionType,
    headless: bool,
    months_before: int = 1,
    months_after: int = 1,
):
    try:
        params = ExtractorExtraParameters(
            headless=headless,
            months_before=months_before,
            months_after=months_after,
            request_interceptor_state=interceptor_state,
        )

        next_time_to_run = time() + 10
        run_at = strftime("%M:%S", localtime(next_time_to_run))

        def my_job():
            asyncio.new_event_loop().run_until_complete(
                scheduled_data_extraction.run(extractor_key, params)
            )
            return schedule.CancelJob

        schedule.every().hour.at(run_at).do(my_job)
    except Exception as e:
        Log.error(f"Error in job: {e}")


def job_waiter(*arks, **kwargs):
    asyncio.new_event_loop().run_until_complete(
        scheduled_data_extraction.run(*arks, **kwargs)
    )


class TaskRunner:
    _thread: threading.Thread
    _stop = False

    def start(self):
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def stop(self):
        self._stop = True
        self._thread.join()

    def run(self):

        # Default task scheduler
        params = ExtractorExtraParameters(
            headless=True,
            months_before=1,
            months_after=1,
            request_interceptor_state=interceptor_state,
        )
        schedule.every().day.at("00:00:00").do(
            job_waiter, DataExtractionType.TIMELINE, params
        )
        params2 = ExtractorExtraParameters(
            headless=True,
            request_interceptor_state=interceptor_state,
        )
        schedule.every().day.at("02:00:00").do(
            job_waiter, DataExtractionType.BATCHES, params2
        )

        try:
            while not self._stop:
                schedule.run_pending()
                sleep(1)
        except (KeyboardInterrupt, SystemExit):
            Log.info("Exiting TaskRunner")
            if self._thread:
                self._thread.join()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--headless", type=int, default=1, choices=[0, 1])
    parser.add_argument(
        "--extractor",
        type=str,
        default="timeline",
        choices=DataExtractionType.__members__.values(),
    )
    parser.add_argument("--months_before", type=int, default=1)
    parser.add_argument("--months_after", type=int, default=1)

    args = parser.parse_args()
    Log.info(f"Running with args: {args}")
    asyncio.run(
        job(
            extractor_key=DataExtractionType[args.extractor.upper()],
            headless=bool(args.headless),
            months_before=args.months_before,
            months_after=args.months_after,
        )
    )
