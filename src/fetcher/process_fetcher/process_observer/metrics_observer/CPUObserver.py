import psutil

from src.fetcher.process_fetcher.process_observer.metrics_observer.ObserverInterface import ObserverInterface
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName


class CPUObserver(ObserverInterface):
    metric_name: MetricName.CPU

    def observe(self, process: psutil.Process) -> Metric:
        return Metric(process.cpu_percent(), self.metric_name)
