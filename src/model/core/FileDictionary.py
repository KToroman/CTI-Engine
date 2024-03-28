from typing import Dict
from src.model.core.CFile import CFile


class FileDictionary:
    """a simple wrapper for a dictionary that stores the cfiles according to name"""

    def __init__(self) -> None:
        self.dictionary: Dict[str, CFile] = {}

    def add_file(self, cfile: CFile) -> CFile:
        self.dictionary[cfile.get_name()] = cfile
        return cfile

    def get_cfile_by_name(self, name: str) -> CFile|None:
        """returns the associated file or creates a new SourceFile with that name & returns it
        if no file has the name 'name'"""
        return self.dictionary.get(name, None)

    def pop_sourcefile_by_name(self, name: str) -> CFile:
        return self.dictionary.pop(name)

    def isInDictionary(self, name: str) -> bool:
        if name in self.dictionary:
            return True
        return False
