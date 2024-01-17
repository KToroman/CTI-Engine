import time

import psutil

from src.model.core import Metric


class ProcessPoint:

    def __init__(self):
        self.process = psutil.Process
        self.timestamp = time
        self.metrics = [Metric]
