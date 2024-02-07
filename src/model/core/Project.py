import time
from typing import List
from src.model.core.CFile import CFile
from src.model.core.FileDictionary import FileDictionary
from src.model.core.SourceFile import SourceFile


class Project:
    """Project models a CMake-Project and represents a tracked project with its tracked CFiles."""

    # TODO maybe we should just delete the list altogether...

    def __init__(self, working_dir: str, origin_pid: int, path_to_save: str):
        self.source_files: List[SourceFile] = list()
        self.working_dir = working_dir
        self.origin_pid = origin_pid
        self.path_to_save = path_to_save
        self.file_dict = FileDictionary()
        self.project_time = time.time() - 0.5

    def get_sourcefile(self, name: str) -> SourceFile:
        file_exists: bool = self.file_dict.isInDictionary(name)
        source_file: SourceFile = self.file_dict.get_file_by_name(name)
        if not file_exists:
            self.source_files.append(source_file)
        return source_file
