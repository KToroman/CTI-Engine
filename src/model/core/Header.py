from src.model.core.CFile import CFile


class Header(CFile):
    """Header is a CFile, models a c-header and is used to represent a tracked header in the program."""
    parent: CFile

    def __init__(self, path: str, parent: CFile) -> None:
        self.build_file_name: str = ""
        self.parent = parent
        super(Header, self).__init__(path)