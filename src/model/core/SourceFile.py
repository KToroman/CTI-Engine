from CFile import CFile


class SourceFile(CFile):
    compile_command: str

    def __init__(self, path: str):
        self.path = path
        self.data_entries = list()
        self.header = list()
