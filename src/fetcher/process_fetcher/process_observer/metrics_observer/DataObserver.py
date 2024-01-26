from typing import List
from psutil import Process
import time

from metrics_observer.RAMObserver import RAMObserver
from metrics_observer.CPUObserver import CPUObserver
from metrics_observer.ObserverInterface import ObserverInterface
from src.model.core.Metric import Metric
from src.model.core.ProcessPoint import ProcessPoint

class DataObserver:
    def __init__(self) -> None:
        self.__observers: List[ObserverInterface] = list()
        self.__observers.append(RAMObserver())
        self.__observers.append(CPUObserver())

    def observe(self, process: Process) -> ProcessPoint:
        timestamps: List[float] = list()
        metrics: List[Metric] = list()
        # since typing doesn't work in for statements:
        observer: ObserverInterface 
        for observer in self.__observers:
            timestamps.append(time.time())
            metrics.append(observer.observe(process))
        timestamp: float = sum(timestamps) / len(timestamps)
        return ProcessPoint(process, timestamp, metrics)

        

