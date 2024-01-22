from src.model.core import SourceFile


class Project(object):
    source_files: [SourceFile]

    def __init__(self, working_dir: str,
                 origin_pid: int,
                 path_to_save: str):
        self.working_dir = working_dir
        self.origin_pid = origin_pid
        self.path_to_save = path_to_save
