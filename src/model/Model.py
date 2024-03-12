import copy
import os.path
from multiprocessing import Event, Queue
from optparse import Option
import time
from typing import List, Optional, cast
from src.exceptions.ProjectNotFoundException import ProjectNotFoundException

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
        self.current_project: Project = None
        self.projects: List[Project] = list()
        self.semaphore_list: List[ProjectFinishedSemaphore] = list()

    def insert_datapoint(self, data_point: DataEntry):
        """inserts datapoint to sourcefile according to their paths to the current project"""
        cfile: CFile = self.current_project.get_sourcefile(data_point.path)
        cfile.data_entries.append(data_point)

    def insert_datapoint_header(self, data_point: DataEntry, current_cfile: CFile = None):
        if current_cfile is None:
            for cfile in self.current_project.source_files:
                self.insert_datapoint_header(data_point, cfile)
        else:
            if current_cfile.path == data_point.path:
                current_cfile.data_entries.append(data_point)
            for header in cast(list[Header], current_cfile.headers):
                self.insert_datapoint_header(data_point, header)

    def project_in_semaphore_list(self, project_dir: str):
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

    def get_semaphore_by_name(self, name) -> ProjectFinishedSemaphore:
        for semaphore in self.semaphore_list:
            if name == semaphore.project_dir:
                return semaphore
        raise Exception

    def add_project(self, project: Project, semaphore: Optional[ProjectFinishedSemaphore]) -> None:
        """adds new project to model"""

        if not self.project_in_list(project.name) and os.getcwd().split("/")[-1] not in project.working_dir:
            self.projects.append(project)
            if semaphore is not None:
                self.semaphore_list.append(semaphore)
            self.current_project = project
            print("[Model]   new project")


    def project_in_list(self, name: str) -> bool:
        for p in self.projects:
            if name == p.name:
                return True
        return False
    def get_sourcefile_by_name(self, name: str) -> SourceFile:
        return self.current_project.get_sourcefile(name)

    def get_current_working_directory(self) -> str:
        if self.current_project is None:
            return ""
        return self.current_project.working_dir

    def get_all_project_names(self) -> List[str]:
        return_list: List[str] = list()
        for project in self.projects:
            return_list.append(project.name)
        return return_list
