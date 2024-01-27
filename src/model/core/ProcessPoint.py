from typing import List

import psutil

from src.model.core.Metric import Metric


class ProcessPoint:
    def __init__(
        self, process: psutil.Process, timestamp: float, metrics: List[Metric]
    ):
        self.process = process
        self.timestamp = timestamp
        self.metrics = metrics
