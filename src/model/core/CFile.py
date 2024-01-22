import time
from abc import ABC

from src.model.core import DataEntry, Header, MetricName
from src.model.core.CFileReadViewInterface import CFileReadViewInterface


class CFile(ABC, CFileReadViewInterface):
    path: str
    data_entries: [DataEntry]
    header: [Header]

    def get_name(self) -> str:
        return self.path

    def get_total_time(self) -> float:
        return self.data_entries[len(self.data_entries)].timestamp.time() - self.data_entries[0].timestamp.time()

    def get_max(self, metric: MetricName) -> float:
        max_entry_value = 0
        for entry in self.data_entries:
            if entry.name == metric:
                if entry.value > max_entry_value:
                    max_entry = entry.value

        return max_entry_value

    def get_metrics(self, metric: MetricName) -> [float]:
        metric_list = []
        for entry in self.data_entries:
            if entry.name == metric:
                metric_list.append(entry.value)

        return metric_list
