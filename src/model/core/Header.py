from typing import List

from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.CFile import CFile


class Header(CFile):
    """Header is a CFile, models a c-header and is used to represent a tracked header in program."""
    def __init__(self, path: str) -> None:
        super().__init__(path)


