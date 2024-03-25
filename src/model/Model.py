import os.path
from multiprocessing import Event, Queue
from typing import Dict, List, Optional, cast
from src.exceptions.CFileNotFoundError import CFileNotFoundError
from src.exceptions.SemaphoreNotFoundException import SemaphoreNotFoundException
from src.exceptions.ProjectNotFoundException import ProjectNotFoundException

from src.model.DataBaseEntry import DataBaseEntry
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.Header import Header
from src.model.core.Project import Project
from src.model.core.ProjectFinishedSemaphore import ProjectFinishedSemaphore
from src.model.core.SourceFile import SourceFile


class Model(ModelReadViewInterface):
    """
    Model class keeps score of all measured data and files
    A model consists of an arbitrary number of projects."""

    def __init__(self) -> None:
        self.current_project: Optional[Project] = None
        self.projects: List[Project] = list()
        self.semaphore_list: List[ProjectFinishedSemaphore] = list()

    def insert_datapoint(self, data_point: DataEntry) -> None:
        """inserts datapoint to sourcefile according to their paths to the current project"""
        if self.current_project is None:
            raise ProjectNotFoundException
        cfile: CFile = self.current_project.get_sourcefile(data_point.path)
        cfile.data_entries.append(data_point)
        self.current_project.add_to_delta(
            path=cfile.path, parent_or_compile_command="", data_entry=data_point, hierarchy_level=0
        )

    def insert_datapoint_header(self, data_entry: DataEntry) -> None:
        """
        if self.current_project is None:
            raise ProjectNotFoundException
        header = self.current_project.get_header_by_name(data_entry.path)
        if header is None:
            raise CFileNotFoundError
        header.data_entries.append(data_entry)
        if self.current_project is None:
            raise ProjectNotFoundException
        parent = header.parent
        if parent is None:
            raise CFileNotFoundError
        """
        header = self.current_project.get_header(data_entry.path,
                                                 self.current_project.get_sourcefile(self.current_project.current_sourcefile))
        if header is not None:
            header.data_entries.append(data_entry)
            self.current_project.add_to_delta(
                path=header.path,
                parent_or_compile_command=header.parent.path,
                data_entry=data_entry,
                hierarchy_level=header.hierarchy_level)

    def project_in_semaphore_list(self, project_dir: str) -> bool:
        for semaphore in self.semaphore_list:
            if project_dir == semaphore.project_dir:
                return True
        return False

    def get_project_by_name(self, name: str) -> Project:
        for project in self.projects:
            if name == project.name:
                return project
        raise ProjectNotFoundException

    def does_project_exist(self, name: str) -> bool:
        for project in self.projects:
            if name == project.working_dir:
                return True
        return False

    def get_semaphore_by_name(self, name: str) -> ProjectFinishedSemaphore:
        for semaphore in self.semaphore_list:
            if name == semaphore.project_name:
                return semaphore
        raise SemaphoreNotFoundException(
            "[Model]   Could not find semaphore for a project."
        )

    def add_project(
            self, project: Project, semaphore: Optional[ProjectFinishedSemaphore]
    ) -> None:
        """adds new project to model"""
        if (not self.project_in_semaphore_list(project.working_dir)
                and os.getcwd().split("/")[-1] not in project.working_dir):
            self.projects.append(project)
            if semaphore is not None:
                self.semaphore_list.append(semaphore)
            self.current_project = project
            print("[Model]  new project")


    def project_in_list(self, name: str) -> bool:
        for p in self.projects:
            if name == p.name:
                return True
        return False

    def get_sourcefile_by_name(self, name: str) -> SourceFile:
        """returns the sourcefile from the current project that matches name"""
        if self.current_project is None:
            raise ProjectNotFoundException
        return self.current_project.get_sourcefile(name)

    def get_current_working_directory(self) -> str:
        if self.current_project is None:
            return ""
        return self.current_project.working_dir

    def get_all_project_names(self) -> List[str]:
        return_list: List[str] = list()
        for project in self.projects:
            if not self.__project_name_in_semaphore(project.name):
                return_list.append(project.name)
        return return_list

    def wait_for_project(self) -> None:
        """Blocks until current_project is available"""
        while self.current_project is None:
            pass

    def get_current_project_name(self) -> str:
        if self.current_project is None:
            raise ProjectNotFoundException
        return self.current_project.name

    def __project_name_in_semaphore(self, name: str) -> bool:
        for semaphore in self.semaphore_list:
            if semaphore.project_name == name:
                return True
        return False