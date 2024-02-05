import copy
import time
from typing import List

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
        self.current_project: Project = None
        self.projects: List[Project] = list()
        self.save_project: Project = None
        self.new_project = False # TODO delete

    def get_project_name(self) -> str:
        """returns the name of the current project"""
        name: str = self.current_project.working_dir + str(
            self.current_project.origin_pid
        )
        return name

    def get_cfiles(self) -> List[CFileReadViewInterface]:
        """returns view only on all cfiles in current project"""
        cfiles_view: List[CFileReadViewInterface] = list()
        cfiles_view.extend(self.current_project.source_files)
        return cfiles_view

    def insert_datapoints(self, data_points: List[DataEntry]):
        """inserts datapoints to sourcefile according to their paths to the current project"""
        for data_point in data_points:
            cfile: CFile = self.current_project.get_sourcefile(data_point.path)
            cfile.data_entries.append(data_point)

    def insert_datapoints_header(self, data_points: List[DataEntry], header: Header):
        for data_point in data_points:
            header.data_entries.append(data_point)

    def add_project(self, project: Project) -> None:
        """adds new project to model"""
        self.projects.append(project)
        self.current_project = project
        self.new_project = True

    def get_sourcefile_by_name(self, name: str) -> SourceFile:
        return self.current_project.get_sourcefile(name)

    def update_save_project(self):
        if self.new_project and self.projects.__len__() >= 2:
            self.save_project = copy.deepcopy(self.projects[self.projects.__len__() - 2])
            self.new_project = False
            return
        self.save_project = copy.deepcopy(self.current_project)

    def get_current_project(self) -> Project: # TODO why was this changed??
        return self.save_project

