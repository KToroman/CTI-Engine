from typing import Protocol

from src.model.core import MetricName


class CFileReadViewInterface(Protocol):

    def get_name(self) -> str:
        """Gets the name of the CFile"""

    def get_total_time(self) -> float:
        """Gets the total time, which the CFile needed to build."""

    def get_max(self, metric: MetricName) -> float:
        """Gets the maximum value of the given metric, which has been tracked."""

    def get_metrics(self, metric: MetricName) -> [float]:
        """Gets all values of the given metric."""
