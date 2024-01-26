from typing import Dict

from model.core.CFile import CFile


class FileDictionary:
    def __init__(self):
        self.dictionary: Dict[str, CFile] = dict()

    def add_file(self, cfile: CFile):
        self.dictionary.update({cfile.get_name: cfile})

    def get_file_by_name(self, name: str) -> CFile:
        return self.dictionary.get(name)

    def pop_file_by_name(self, name: str) -> CFile:
        return self.dictionary.pop(name)
