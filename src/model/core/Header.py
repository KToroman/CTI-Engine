from typing import List, Optional
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry


class Header(CFile):
    """Header is a CFile, models a c-header and is used to represent a tracked header in the program."""

    parent: Optional[CFile]

    def __init__(
        self, path: str, parent: Optional[CFile], hierarchy_level: int
    ) -> None:
        self.data_entries: List[DataEntry] = []
        self.headers: List[CFileReadViewInterface] = []
        self.path: str = path
        self.error: bool = False
        self.build_file_name: str = ""
        self.parent = parent
        self.hierarchy_level: int = hierarchy_level
        self.sorted_timestamp_list = None
