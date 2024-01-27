from model.core.CFile import CFile
from model.core.FileDictionary import FileDictionary
from src.model.core import SourceFile


class Project(object):
    source_files: [SourceFile] = list()

    def __init__(self, working_dir: str,
                 origin_pid: int,
                 path_to_save: str):
        self.working_dir = working_dir
        self.origin_pid = origin_pid
        self.path_to_save = path_to_save
        self.file_dict = FileDictionary()

    def get_cfile(self, name: str) -> CFile:
        return self.file_dict.get_file_by_name(name)
