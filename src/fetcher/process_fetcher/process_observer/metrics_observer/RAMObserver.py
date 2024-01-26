import psutil

from src.fetcher.process_fetcher.process_observer.metrics_observer.ObserverInterface import ObserverInterface
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName


class RAMObserver(ObserverInterface):
    metric_name = MetricName.RAM

    def observe(self, process: psutil.Process) -> Metric:
        return Metric(process.memory_info().rss, self.metric_name)

