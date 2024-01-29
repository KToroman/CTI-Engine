from typing import List

from CFileReadViewInterface import CFileReadViewInterface
from DataEntry import DataEntry
from CFile import CFile


class Header(CFile):
    """Header is a CFile, models a c-header and is used to represent a tracked header in program."""
    def __init__(self, path: str):
        self.path: str = path
        self.data_entries: List[DataEntry] = list()
        self.header: List[CFileReadViewInterface] = list()

    def get_timestamps(self) -> List[float]:
        timestamps: List[float] = list()
        for datapoint in self.data_entries:
            timestamps.append(datapoint.timestamp)
        return timestamps
