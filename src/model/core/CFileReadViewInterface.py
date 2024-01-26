from abc import ABC, abstractmethod

import MetricName


class CFileReadViewInterface(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_total_time(self) -> float:
        pass

    @abstractmethod
    def get_max(self, metric: MetricName) -> float:
        pass

    @abstractmethod
    def get_metrics(self, metric: MetricName) -> [float]:
        pass
