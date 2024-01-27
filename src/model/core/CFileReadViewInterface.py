
from typing import Protocol, List

from MetricName import MetricName


class CFileReadViewInterface(Protocol):

    def get_name(self) -> str:
        pass

    def get_total_time(self) -> float:
        pass

    def get_max(self, metric: MetricName) -> float:
        pass

    def get_metrics(self, metric: MetricName) -> List[float]:
        pass
