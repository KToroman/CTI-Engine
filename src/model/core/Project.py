import time
from typing import List, Optional
from src.exceptions.CFileNotFoundError import CFileNotFoundError
from src.model.DataBaseEntry import DataBaseEntry
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.FileDictionary import FileDictionary
from src.model.core.Header import Header
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

    def get_sourcefile(self, name: str) -> CFile:
        cfile = self.file_dict.get_cfile_by_name(name)
        if cfile is None:
            cfile = SourceFile(path=name)
            self.file_dict.add_file(cfile)
            self.source_files.append(cfile)
        return cfile
    
    def get_header_by_name(self, name: str) -> CFile:
        cfile = self.file_dict.get_cfile_by_name(name)
        if cfile is None:
            cfile = Header(name, None, 1)
            self.file_dict.add_file(cfile)
        return cfile
    
    def get_unkown_cfile(self, path: str, hierarchy_level: int) -> CFile:
        cfile = self.file_dict.get_cfile_by_name(path)
        if cfile is None:
            if hierarchy_level > 0:
                cfile = SourceFile(path=path)
                self.file_dict.add_file(cfile)
            else:
                cfile = Header(path, None, 1)
                self.file_dict.add_file(cfile)

        return cfile

    def update_header(self, header_path: str, parent_path: str, hierarchy_level: int):
        header = self.get_header_by_name(header_path)
        parent = self.get_unkown_cfile(path=parent_path, hierarchy_level=hierarchy_level-1)
        header.parent = parent
        parent.headers.append(header)
        header.hierarchy_level = hierarchy_level
        self.add_to_delta(hierarchy_level=hierarchy_level, path=header_path, parent_path=parent_path, data_entry=None)

    def update_source_file(self, path):
        self.get_sourcefile(path)
        self.add_to_delta(hierarchy_level=0, path=path, parent_path="", data_entry=None)



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
