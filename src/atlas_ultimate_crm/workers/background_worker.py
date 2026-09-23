import logging
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class BackgroundWorker(QThread):
    """Qt-integrated background worker for non-blocking operations."""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.error("BackgroundWorker error: %s", e)
            self.error.emit(str(e))
