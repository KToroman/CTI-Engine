import datetime
import time
from typing import List, Optional, Protocol

from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.MetricName import MetricName


class CFile(CFileReadViewInterface, Protocol):
    """Models CFile and is used for representing a tracked CFile in program"""

    data_entries: List[DataEntry]
    headers: List[CFileReadViewInterface]
    path: str
    error: bool

    def __init__(self, path: str) -> None:
        raise NotImplementedError

    def get_name(self) -> str:
        return self.path

    def get_total_time(self) -> float:
        print("[CFile]      getting total time...")
        print(len(self.data_entries))
        sorted_timestamp_list = sorted(
            self.data_entries, key=lambda data_entry: data_entry.timestamp
        )
        print(len(sorted_timestamp_list))
        if sorted_timestamp_list:
            return (
                sorted_timestamp_list[-1].timestamp -
                sorted_timestamp_list[0].timestamp
            )
        return 0

    def get_max(self, metric_name: MetricName) -> float:
        max_entry_value = 0
        for entry in self.data_entries:
            for metric in entry.metrics:
                if metric.name == metric_name:
                    if metric.value > max_entry_value:
                        max_entry_value = metric.value

        return max_entry_value

    def get_metrics(self, metric_name: MetricName) -> List[float]:
        metric_list: List[float] = list()
        sorted_timestamp_list = sorted(
            self.data_entries, key=lambda data_entry: data_entry.timestamp
        )
        for entry in sorted_timestamp_list:
            for metric in entry.metrics:
                if metric.name == metric_name:
                    metric_list.append(metric.value)

        return metric_list

    def __str__(self) -> str:
        return f"Path: {self.path} \nHeaders: {[a.get_name()  for a in self.headers]}"

    def get_header_by_name(self, name: str) -> Optional[CFileReadViewInterface]:
        for header in self.headers:
            if header.get_name is name:
                return header
        return None

    def get_timestamps(self) -> List[float]:
        timestamps: List[float] = list()
        sorted_timestamp_list = sorted(
            self.data_entries, key=lambda data_entry: data_entry.timestamp
        )
        for datapoint in sorted_timestamp_list:
            timestamps.append(datapoint.timestamp)
        return timestamps

    def get_headers(self):
        return self.headers

    def has_error(self) -> bool:
        return self.error
