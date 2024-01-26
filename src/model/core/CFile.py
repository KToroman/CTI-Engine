from typing import List, Protocol

from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.MetricName import MetricName


class CFile(CFileReadViewInterface, Protocol):
    data_entries: List[DataEntry] = []
    header: List[CFileReadViewInterface] = []

    def __init__(self, path: str):
        self.path = path

    def get_name(self) -> str:
        return self.path

    def get_total_time(self) -> float:
        return self.data_entries[len(self.data_entries)-1].timestamp - self.data_entries[0].timestamp

    def get_max(self, metric: MetricName) -> float:
        max_entry_value = 0
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric:
                    if metric.value > max_entry_value:
                        max_entry_value = metric.value

        return max_entry_value

    def get_metrics(self, metric: MetricName) -> List[float]:
        metric_list = []
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric:
                    metric_list.append(metric.value)

        return metric_list
