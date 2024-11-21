import signal
from types import FrameType
from typing import Any, Callable

from src.infra.core.logging import Log


class GracefulKiller:
    kill_now = False
    funcs: list[Callable[[int, FrameType | None], Any]] = []

    def __init__(self, funcs: list[Callable[[int, FrameType | None], Any]]):
        self.funcs = funcs
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        Log.info("Received signal to exit")
        for func in self.funcs:
            func(signum, frame)

        self.kill_now = True
        exit(1)
