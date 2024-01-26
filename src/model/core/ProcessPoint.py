import time
from typing import List

import psutil

from src.model.core.Metric import Metric


class ProcessPoint:
    metrics: List[Metric] = list()

    def __init__(self, process: psutil.Process,
                 timestamp: float):
        self.process = process
        self.timestamp = timestamp
