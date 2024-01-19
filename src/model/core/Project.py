from src.model.core import SourceFile


class Project(object):
    working_dir: str
    origin_pid: int
    path_to_save: str
    source_files: [SourceFile]

    def __init__(self):
        pass
