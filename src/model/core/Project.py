import time
from typing import List
from src.model.core.CFile import CFile
from src.model.core.FileDictionary import FileDictionary
from src.model.core.SourceFile import SourceFile


class Project:
    """Project models a CMake-Project and represents a tracked project with its tracked CFiles."""

    __DEFAULT_PATH_TO_SAVE = ""

    def __init__(self, working_dir: str, name: str, path_to_save: str = __DEFAULT_PATH_TO_SAVE):
        self.source_files: List[SourceFile] = list()
        self.working_dir = working_dir
        self.name = name
        self.file_dict = FileDictionary()
        self.project_time = time.time() - 0.5
        self.path_to_save = f"{path_to_save}/{self.working_dir}/{self.project_time}"

    def get_sourcefile(self, name: str) -> SourceFile:
        file_exists: bool = self.file_dict.isInDictionary(name)
        source_file: SourceFile = self.file_dict.get_sourcefile_by_name(name)
        if not file_exists:
            self.source_files.append(source_file)
        return source_file
