from typing import List, Optional

from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric


class DataBaseEntry:
    def __init__(
        self,
        path: str,
        parent: str,
        timestamp: Optional[float],
        metrics: Optional[List[Metric]],
        hierarchy_level: int,
    ):
        self.path: str = path
        self.parent: str = parent
        self.timestamp: Optional[float] = timestamp
        self.metrics: Optional[List[Metric]] = metrics
        assert hierarchy_level < 3 and hierarchy_level >= 0
        self.hierarchy_level: int = hierarchy_level
