from typing import List

import psutil

from src.fetcher.process_fetcher.CProcess import CProcess
from src.model.core.Metric import Metric


class ProcessPoint:
    """ProcessPoint stores a psutil process and its measured values."""
    def __init__(
        self, process: CProcess, timestamp: float, metrics: List[Metric]
    ):
        self.process = process
        self.timestamp = timestamp
        self.metrics = metrics
