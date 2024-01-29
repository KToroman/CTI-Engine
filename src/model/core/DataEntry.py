from typing import List

from Metric import Metric


class DataEntry:
    """DataEntry is used to represent a single measurement for a CFIle."""
    def __init__(self, path: str, timestamp: float, metrics: List[Metric]):
        self.path = path
        self.timestamp = timestamp
        self.metrics = metrics
