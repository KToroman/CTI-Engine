import abc
from abc import ABC

import psutil

from src.model.core.Metric import Metric


class ObserverInterface(ABC):

    @abc.abstractmethod
    def observe(self, process: psutil.Process) -> Metric:
        pass
