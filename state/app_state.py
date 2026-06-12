from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
import time


@dataclass
class LiveMetrics:
    total_vulns: int = 0
    unique_vulns: int = 0
    processing_time: int = 0
    success_rate: int = 0
    _started_at: float | None = None
    _subs: list[Callable[["LiveMetrics"], None]] = field(default_factory=list)

    def subscribe(self, fn: Callable[["LiveMetrics"], None]):
        self._subs.append(fn)

    def notify(self):
        for fn in self._subs:
            fn(self)

    def reset(self):
        self.total_vulns = 0
        self.unique_vulns = 0
        self.processing_time = 0
        self.success_rate = 0
        self._started_at = None
        self.notify()

    def start(self):
        self.processing_time = 0
        self.success_rate = 0
        self._started_at = time.time()
        self.notify()

    def tick(self):
        if self._started_at is not None:
            self.processing_time = int(time.time() - self._started_at)
            self.notify()

    def stop(self, success: bool = True):
        if self._started_at is not None:
            self.processing_time = int(time.time() - self._started_at)
        self.success_rate = 100 if success else 0
        self._started_at = None
        self.notify()
