import time
from typing import List
import typing
from src.model.DataBaseEntry import DataBaseEntry
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.FileDictionary import FileDictionary
from src.model.core.Header import Header
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
        self.file_dict: FileDictionary = FileDictionary()
        self.project_time: float = time.time() - 0.5
        time_stamp = str(self.project_time).split(".")
        time_stamp_str = f"{time_stamp[0]}_{time_stamp[1]}"
        self.path_to_save = f"{path_to_save}/{self.working_dir}/CTI_Engine_{time_stamp_str}"
        self.delta_entries: List[DataBaseEntry] = list()
        self.count_headers = 0
        self.__failed: bool = False
        self.current_sourcefile: str = ""

    def get_sourcefile(self, name: str) -> SourceFile:
        cfile = self.file_dict.get_cfile_by_name(name)
        if cfile is None:
            cfile = SourceFile(path=name)
            self.file_dict.add_file(cfile)
            self.source_files.append(cfile)
            if self.__failed:
                cfile.error = True
        return typing.cast(SourceFile, cfile)

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

    def set_failed(self):
        self.__failed = True
        for source_files in self.source_files:
            if source_files.compile_command == "":
                source_files.error = True

    def update_headers(self, header: Header, parent: CFile, hierarchy: int):
        if hierarchy > 2:
            return
        new_header = Header(header.path, parent, hierarchy)
        parent.headers.append(new_header)
        self.file_dict.add_file(new_header)
        self.add_to_delta(hierarchy_level=hierarchy, path=new_header.path,
                          parent_or_compile_command=parent.path,
                          data_entry=None)
        for headers in header.headers:
            self.update_headers(headers, new_header, hierarchy + 1)

    def update_source_file(self, path, compile_command: str) -> CFile:
        source_file = typing.cast(SourceFile, self.get_sourcefile(path))
        source_file.compile_command = compile_command
        self.add_to_delta(hierarchy_level=0, path=path,
                          parent_or_compile_command=compile_command, data_entry=None)
        return source_file

    def add_to_delta(
            self, hierarchy_level: int, path: str, parent_or_compile_command: str, data_entry: DataEntry | None
    ) -> None:
        if data_entry is None:
            self.delta_entries.append(DataBaseEntry(
                path, parent_or_compile_command, None, None, hierarchy_level))
        else:
            self.delta_entries.append(
                DataBaseEntry(
                    path,
                    parent_or_compile_command,
                    data_entry.timestamp,
                    data_entry.metrics,
                    hierarchy_level,
                )
            )

    def get_project_time(self) -> float:
        """returns project's first measured timestamp"""
        starting_points: list[float] = list()
        for source_file in self.source_files:
            if source_file.get_min_timestamps() > 0:
                starting_points.append(source_file.get_min_timestamps())
        starting_points.sort()

        if starting_points:
            return starting_points[0]
        else:
            return 0

    def get_project_name(self) -> str:
        return self.name

    def get_cfiles(self) -> List[CFileReadViewInterface]:
        cfiles_view: List[CFileReadViewInterface] = list()
        cfiles_view.extend(self.source_files)
        return cfiles_view

    def __str__(self) -> str:
        return f"<Project '{self.name}' with dir '{self.working_dir}'>"

    def get_header(self, name: str, parent: CFile):
        for header in parent.headers:
            if header.get_name() == name and not header.has_been_build:
                return header
            temp = self.get_header(name, header)
            if temp is not None:
                return temp
