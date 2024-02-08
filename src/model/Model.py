import copy
import os.path
from optparse import Option
import time
from typing import List, Optional
from src.exceptions.ProjectNotFoundException import ProjectNotFoundException

from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.Header import Header
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile


class Model(ModelReadViewInterface):
    """
    Model class keeps score of all measured data and files
    A model consists of an arbitrary number of projects."""

    def __init__(self) -> None:
        self.current_project: Project = Project("")
        self.projects: List[Project] = list()

    def get_project_name(self) -> str:
        """returns the name of the current project"""
        name: str = self.current_project.path_to_save
        return name

    def get_cfiles(self) -> List[CFileReadViewInterface]:
        """returns view only on all cfiles in current project"""
        cfiles_view: List[CFileReadViewInterface] = list()
        cfiles_view.extend(self.current_project.source_files)
        print(cfiles_view.__len__())
        return cfiles_view

    def insert_datapoint(self, data_point: DataEntry):
        """inserts datapoint to sourcefile according to their paths to the current project"""
        cfile: CFile = self.current_project.get_sourcefile(data_point.path)
        cfile.data_entries.append(data_point)

    def insert_datapoints_header(self, data_points: List[DataEntry], header: Header):
        for data_point in data_points:
            header.data_entries.append(data_point)

    def get_project_by_name(self, name: str) -> Project:
        for project in self.projects:
            if name == project.working_dir:
                return project
        raise ProjectNotFoundException

    def does_project_exist(self, name: str) -> bool:
        for project in self.projects:
            if name == project.working_dir:
                return True
        return False

    def add_project(self, project: Project) -> None:
        """adds new project to model"""

        if not self.does_project_exist(project.working_dir) and "/src/app" not in project.working_dir:
            self.projects.append(project)
            self.current_project = project

    def get_sourcefile_by_name(self, name: str) -> SourceFile:
        return self.current_project.get_sourcefile(name)

    def get_current_project(self) -> Optional[Project]:
        try:
            return copy.deepcopy(self.current_project)
        except:
            return None

    def get_project_time(self) -> float:
        return self.current_project.project_time
    
    def get_current_working_directory(self) -> str:
        if self.current_project is not None:
            return self.current_project.working_dir
        return ""
