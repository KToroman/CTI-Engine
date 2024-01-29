from typing import List
from CFile import CFile
from CFileReadViewInterface import CFileReadViewInterface
from DataEntry import DataEntry


class SourceFile(CFile):
    """SourceFile is a CFile, represents a c-sourcefile and is used to represent a tracked sourcefile in program."""
    compile_command: str

    def __init__(self, path: str):
        self.path: str = path
        self.data_entries: List[DataEntry] = list()
        self.header: List[CFileReadViewInterface] = list()
