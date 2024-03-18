import time
from typing import List, Optional
from src.model.DataBaseEntry import DataBaseEntry
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.FileDictionary import FileDictionary
from src.model.core.ProjectFinishedSemaphore import ProjectFinishedSemaphore
from src.model.core.ProjectReadViewInterface import ProjectReadViewInterface
from src.model.core.SourceFile import SourceFile


class Project(ProjectReadViewInterface):
    """Project models a CMake-Project and represents a tracked project with its tracked CFiles."""

    __DEFAULT_PATH_TO_SAVE = ""

    def __init__(
        self, working_dir: str, name: str, path_to_save: str = __DEFAULT_PATH_TO_SAVE
    ):
        self.source_files: List[SourceFile] = list()
        self.working_dir = working_dir
        self.name = name
        self.file_dict = FileDictionary()
        self.project_time = time.time() - 0.5
        time_stamp = str(self.project_time).split(".")
        time_stamp_str = f"{time_stamp[0]}_{time_stamp[1]}"
        self.path_to_save = f"{path_to_save}/{self.working_dir}/CTI_Engine_{time_stamp_str}"
        self.delta_entries: List[DataBaseEntry] = list()

    def get_sourcefile(self, name: str) -> SourceFile:
        file_exists: bool = self.file_dict.isInDictionary(name)
        source_file: SourceFile = self.file_dict.get_sourcefile_by_name(name)
        if not file_exists:
            self.source_files.append(source_file)
        return source_file

    def add_to_delta(
        self, hierarchy_level: int, path: str, parent_path: str, data_entry: DataEntry
    ):
        self.delta_entries.append(
            DataBaseEntry(
                path,
                parent_path,
                data_entry.timestamp,
                data_entry.metrics,
                hierarchy_level,
            )
        )

    def get_project_time(self) -> float:
        return self.project_time

    def get_project_name(self) -> str:
        return self.name

    def get_cfiles(self) -> List[CFileReadViewInterface]:
        cfiles_view: List[CFileReadViewInterface] = list()
        cfiles_view.extend(self.source_files)
        return cfiles_view

    def __str__(self) -> str:
        return f"<Project '{self.name}' with dir '{self.working_dir}'>"
