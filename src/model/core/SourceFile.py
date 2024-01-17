from src.model.core.CFile import CFile


class SourceFile(CFile):

    def __init__(self):
        super.__init__(self)
        self.compile_command = str

