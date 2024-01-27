from MetricName import MetricName


class Metric:
    def __init__(self, value: float, name: MetricName):
        self.value = value
        self.name = name
