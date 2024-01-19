import time

from src.model.core import Metric


class DataEntry:
    path: str
    timestamp: time
    metrics: [Metric]

    def __init__(self):
        pass
