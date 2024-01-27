from typing import List
from CFile import CFile
from CFileReadViewInterface import CFileReadViewInterface
from DataEntry import DataEntry


class SourceFile(CFile):
    compile_command: str

    def __init__(self, path: str):
        self.path: str = path
        self.data_entries: List[DataEntry] = list()
        self.header: List[CFileReadViewInterface] = list()
