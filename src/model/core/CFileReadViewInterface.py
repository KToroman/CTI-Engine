from typing import Protocol, List

from src.model.core.MetricName import MetricName

'''This interface provides a view on a CFile'''


class CFileReadViewInterface(Protocol):
    def get_name(self) -> str:
        """Returns the path form CFile, by which CFiles are sorted by."""
        raise NotImplementedError

    def get_total_time(self) -> float:
        """Returns the total time a CFile needed to build."""
        raise NotImplementedError

    def get_max(self, metric: MetricName) -> float:
        """Returns the maximum tracked value of a metric."""
        raise NotImplementedError

    def get_metrics(self, metric: MetricName) -> List[float]:
        """Returns all the values tracked from the given metric."""
        raise NotImplementedError

    def get_timestamps(self) -> List[float]:
        """Returns every timestamp tracked for that CFile."""
        raise NotImplementedError

    def get_headers(self):
        raise NotImplementedError

    def has_error(self) -> bool:
        """Returns true if there is an error in this CFile."""
        pass
