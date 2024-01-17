from src.model.core import SourceFile


class Project(object):
    def __init__(self):
        self.working_dir = str
        self.origin_pid = int
        self.path_to_save = str
        self.source_files = [SourceFile]
