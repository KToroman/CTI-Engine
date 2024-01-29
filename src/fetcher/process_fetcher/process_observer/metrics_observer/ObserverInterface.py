from typing import Protocol

import psutil

from src.model.core.Metric import Metric


class ObserverInterface(Protocol):
    """ObserverInterface is used to get metrics from process."""

    def observe(self, process: psutil.Process) -> Metric:
        """Observes the give process for a metric."""
