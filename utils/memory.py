"""Memory lifecycle helpers for heavy tab workflows."""

from __future__ import annotations

import gc
import tracemalloc
from contextlib import contextmanager


@contextmanager
def memory_session(logger, label: str):
    """Track peak memory during one task and force cleanup at the end."""
    started_here = not tracemalloc.is_tracing()
    if started_here:
        tracemalloc.start()

    start_current, start_peak = tracemalloc.get_traced_memory()
    logger.info("[%s] memory start: current=%d KB peak=%d KB", label, start_current // 1024, start_peak // 1024)

    try:
        yield
    finally:
        gc.collect()
        end_current, end_peak = tracemalloc.get_traced_memory()
        logger.info("[%s] memory end: current=%d KB peak=%d KB", label, end_current // 1024, end_peak // 1024)
        if started_here:
            tracemalloc.stop()


def release_large_objects(namespace: dict, names: list[str]):
    """Delete known large objects and collect garbage."""
    for name in names:
        if name in namespace:
            try:
                del namespace[name]
            except Exception:
                pass
    gc.collect()
