from typing import List, Protocol

from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.MetricName import MetricName


class CFile(CFileReadViewInterface, Protocol):
    """Models CFile and is used for representing a tracked CFile in program"""
    data_entries: List[DataEntry] = None
    header: List[CFileReadViewInterface] = None
    path: str = None

    def get_name(self) -> str:
        return self.path

    def get_total_time(self) -> float:
        return (
                self.data_entries[len(self.data_entries) - 1].timestamp
                - self.data_entries[0].timestamp
        )

    def get_max(self, metric: MetricName) -> float:
        max_entry_value = 0
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric:
                    if metric.value > max_entry_value:
                        max_entry_value = metric.value

        return max_entry_value

    def get_metrics(self, metric: MetricName) -> List[float]:
        metric_list: List[float] = list()
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric:
                    metric_list.append(metric.value)

        return metric_list

    def __str__(self) -> str:
        return f"Path: {self.path} \nHeaders: {[a.get_name()  for a in self.header]}"
