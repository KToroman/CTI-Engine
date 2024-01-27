from typing import List

from Metric import Metric


class DataEntry:
    path: str
    timestamp: float
    metrics: List[Metric] = list()


