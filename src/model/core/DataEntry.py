from typing import List

from Metric import Metric


class DataEntry:
    def __init__(self, path: str, timestamp: float, metrics: List[Metric]):
        self.path = path
        self.timestamp = timestamp
        self.metrics = metrics
