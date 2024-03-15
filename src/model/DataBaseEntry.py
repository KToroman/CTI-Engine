from typing import List, Optional

from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric


class DataBaseEntry:
    def __init__(
        self,
        source_file: str,
        header: str,
        timestamp: Optional[float],
        metrics: Optional[List[Metric]],
    ):
        self.source_file: str = source_file
        self.header: str = header
        self.timestamp: Optional[float] = timestamp
        self.metrics: Optional[List[Metric]] = metrics

    def extract_data_entry(self) -> Optional[DataEntry]:
        if self.header != "":
            path = self.header
        else:
            path: str = self.source_file
        if self.timestamp is None or self.metrics is None:
            return None
        else:
            data_entry: DataEntry = DataEntry(
                path=path, timestamp=self.timestamp, metrics=self.metrics
            )
            return data_entry
