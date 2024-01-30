from src.model.core.MetricName import MetricName


class Metric:
    """Metric is used to give a value a name, thus providing a tracked metric."""
    def __init__(self, value: float, name: MetricName):
        self.value = value
        self.name = name
