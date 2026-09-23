import logging
import queue
import threading
import uuid
from typing import Any, Callable

logger = logging.getLogger(__name__)


class LocalTaskQueue:
    """Simple in-process task queue using threads. No Redis/Celery required."""

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue()
        self._worker_thread: threading.Thread | None = None
        self._running = False

    def enqueue(self, func: Callable, *args: Any, **kwargs: Any) -> str:
        job_id = str(uuid.uuid4())
        self._queue.put((job_id, func, args, kwargs))
        return job_id

    def start(self) -> None:
        self._running = True
        self._worker_thread = threading.Thread(target=self._run, daemon=True)
        self._worker_thread.start()
        logger.info("LocalTaskQueue started")

    def stop(self) -> None:
        self._running = False
        if self._worker_thread:
            self._queue.put(None)  # sentinel
            self._worker_thread.join(timeout=5)
        logger.info("LocalTaskQueue stopped")

    def _run(self) -> None:
        while self._running:
            try:
                item = self._queue.get(timeout=1)
                if item is None:
                    break
                job_id, func, args, kwargs = item
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.error("Task %s failed: %s", job_id, e)
            except queue.Empty:
                continue
