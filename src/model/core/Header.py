from typing import Optional
from src.model.core.CFile import CFile


class Header(CFile):
    """Header is a CFile, models a c-header and is used to represent a tracked header in the program."""

    parent: Optional[CFile]

    def __init__(
        self, path: str, parent: Optional[CFile], hierarchy_level: int
    ) -> None:
        self.build_file_name: str = ""
        self.parent = parent
        self.hierarchy_level: int = hierarchy_level
        super(Header, self).__init__(path)
