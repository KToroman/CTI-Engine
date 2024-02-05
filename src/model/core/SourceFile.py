from typing import List
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry


class SourceFile(CFile):
    """SourceFile is a CFile, represents a c-sourcefile and is used to represent a tracked sourcefile in program."""
    compile_command: str

    def __init__(self, path: str):
        self.path: str = path
        self.data_entries: List[DataEntry] = list()
        self.header: List[CFileReadViewInterface] = list()

    def get_timestamps(self) -> List[float]:
        timestamps: List[float] = list()
        for datapoint in self.data_entries:
            timestamps.append(datapoint.timestamp)
        return timestamps
