from src.model.core.CFile import CFile


class SourceFile(CFile):
    compile_command = str

    def __init__(self):
        super(SourceFile, self).__init__()
