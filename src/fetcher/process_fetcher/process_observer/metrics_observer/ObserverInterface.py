from typing import Protocol

import psutil

from src.fetcher.process_fetcher.CProcess import CProcess
from src.model.core.Metric import Metric


class ObserverInterface(Protocol):
    """ObserverInterface is used to get metrics from process."""

    def observe(self, process: CProcess) -> Metric:
        """Observes the give process for a metric."""
