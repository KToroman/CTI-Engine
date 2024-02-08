from typing import Dict

from src.model.core.SourceFile import SourceFile


class FileDictionary:
    """a simple wrapper for a dictionary that stores the cfiles according to name"""

    def __init__(self):
        self.dictionary: Dict[str, SourceFile] = {}

    def add_file(self, sourcefile: SourceFile) -> SourceFile:
        self.dictionary.update({sourcefile.get_name(): sourcefile})
        return sourcefile

    def get_sourcefile_by_name(self, name: str) -> SourceFile:
        """returns the associated file or creates a new SourceFile with that name & returns it
        if no file has the name 'name'"""
        return self.dictionary.get(name) or self.add_file(SourceFile(name))

    def pop_sourcefile_by_name(self, name: str) -> SourceFile:
        return self.dictionary.pop(name)

    def isInDictionary(self, name: str) -> bool:
        if name in self.dictionary:
            return True
        return False
