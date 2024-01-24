import time
from typing import List

from src.model.core import Metric


class DataEntry:
    path: str
    timestamp: float
    metrics: List[Metric]

