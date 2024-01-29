from enum import Enum


class MetricName(Enum):
    """MetricName is used to set the type of metrics tracked."""
    RAM = "RAM"
    CPU = "CPU"
