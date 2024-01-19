import time

import psutil

from src.model.core import Metric


class ProcessPoint:
    process: psutil.Process
    timestamp: time
    metrics: [Metric]

    def __init__(self):
        pass
