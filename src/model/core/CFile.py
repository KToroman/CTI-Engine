import time
from abc import ABC
from typing import List

from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.Header import Header
from src.model.core.MetricName import MetricName


class CFile(ABC, CFileReadViewInterface):
    path: str
    data_entries: List[DataEntry]
    header: List[Header]

    def get_name(self) -> str:
        return self.path

    def get_total_time(self) -> float:
        return self.data_entries[len(self.data_entries)].timestamp - self.data_entries[0].timestamp

    def get_max(self, metric: MetricName) -> float:
        max_entry_value = 0
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric:
                    if metric.value > max_entry_value:
                        max_entry_value = metric.value

        return max_entry_value

    def get_metrics(self, metric: MetricName) -> [float]:
        metric_list = []
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric:
                    metric_list.append(metric.value)

        return metric_list
