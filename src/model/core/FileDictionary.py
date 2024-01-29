from typing import Dict

from CFile import CFile
from SourceFile import SourceFile


class FileDictionary:
    """a simple wrapper for a dictionary that stores the cfiles according to name"""

    def __init__(self):
        self.dictionary: Dict[str, CFile] = {}

    def add_file(self, cfile: CFile):
        self.dictionary.update({cfile.get_name(): cfile})
        return cfile

    def get_file_by_name(self, name: str) -> CFile:
        """returns the associated file or creates a new SourceFile with that name & returns it
        if no file has the name 'name'"""
        return self.dictionary.get(name) or self.add_file(SourceFile(name))

    def pop_file_by_name(self, name: str) -> CFile:
        return self.dictionary.pop(name)

