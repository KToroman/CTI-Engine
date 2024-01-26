import time
from typing import List

import psutil

from src.model.core import Metric


class ProcessPoint:
    metrics: List[Metric] = []

    def __init__(self, process: psutil.Process,
                 timestamp: float):
        self.process = process
        self.timestamp = timestamp
