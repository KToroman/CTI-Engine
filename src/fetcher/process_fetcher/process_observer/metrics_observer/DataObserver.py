import time

import psutil

from src.fetcher.process_fetcher.process_observer.metrics_observer.CPUObserver import CPUObserver
from src.fetcher.process_fetcher.process_observer.metrics_observer.ObserverInterface import ObserverInterface
from typing import List

from src.fetcher.process_fetcher.process_observer.metrics_observer.RAMObserver import RAMObserver
from src.model.core.ProcessPoint import ProcessPoint


class DataObserver:
    observer: List[ObserverInterface] = [RAMObserver(), CPUObserver()]

    def observe(self, process: psutil.Process) -> ProcessPoint:
        process_point = ProcessPoint(process, time.time())
        for observer in self.observer:
            process_point.metrics.append(observer.observe(process))
        return process_point
