import time
from abc import ABC

from src.model.core import DataEntry, Header, MetricName
from src.model.core.CFileReadViewInterface import CFileReadViewInterface


class CFile(ABC, CFileReadViewInterface):
    path: str
    data_entries: [DataEntry]
    header: [Header]

    def __init__(self):
        pass

    def get_name(self) -> str:
        return self.path

    def get_total_time(self) -> float:
        temp_low = time
        temp_high = time

        for entry in self.data_entries:
            if temp_low is None:
                temp_low = entry.timestamp
                temp_high = entry.timestamp
                continue

            if entry.timestamp < temp_low:
                temp_low = entry.timestamp
                continue
            elif entry.timestamp > temp_high:
                temp_high = entry.timestamp
                continue

        return temp_high.time() - temp_low.time()

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
