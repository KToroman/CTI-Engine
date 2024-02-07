from typing import List
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry


class SourceFile(CFile):
    """SourceFile is a CFile, represents a c-sourcefile and is used to represent a tracked sourcefile in program."""

    def __init__(self, path: str):
        super(SourceFile, self).__init__(path)
        self.compile_command: str = ""
