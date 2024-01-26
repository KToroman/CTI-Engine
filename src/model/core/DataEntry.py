from typing import List

from src.model.core.Metric import Metric


class DataEntry:
    path: str
    timestamp: float
    metrics: List[Metric] = list()


