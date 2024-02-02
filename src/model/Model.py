import copy
import time
from typing import List

from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.Project import Project
from src.model.core.FileDictionary import FileDictionary
from src.model.core.SourceFile import SourceFile


class Model(ModelReadViewInterface):
    """
    Model class keeps score of all measured data and files
    A model consists of an arbitrary number of projects,"""

    def __init__(self) -> None:
        self.current_project: Project = None
        self.projects: List[Project] = list()
        self.save_project: Project = None
        self.new_project = False

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

    def insert_datapoints(self, data_points: List[DataEntry], pid: int):

        """inserts datapoints according to their paths to the current project"""
        project = self.get_project(pid)

        for data_point in data_points:
            cfile: CFile = project.get_sourcefile(data_point.path)
            cfile.data_entries.append(data_point)

    def get_project(self, pid: int) -> Project:
        for p in self.projects:
            if p.origin_pid == pid:
                return p
        return None

    def add_project(self, project: Project) -> None:
        """adds new project to model"""
        self.projects.append(project)
        self.current_project = project
        self.new_project = True

    def get_sourcefile_by_name(self, name: str) -> SourceFile:
        return self.current_project.get_sourcefile(name)

    def get_current_project(self, pid: int) -> Project:
        return copy.deepcopy(self.get_project(pid))
