from src.model.core.CFile import CFile


class Header(CFile):
    """Header is a CFile, models a c-header and is used to represent a tracked header in the program."""

    def __init__(self, path: str) -> None:
        self.build_file_name: str = ""
        super(Header, self).__init__(path)