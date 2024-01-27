from typing import List

from ModelReadViewInterface import ModelReadViewInterface
from model.core.CFile import CFile
from model.core.CFileReadViewInterface import CFileReadViewInterface
from core.DataEntry import DataEntry
from core.Project import Project
from model.core.FileDictionary import FileDictionary


class Model(ModelReadViewInterface):
    """
    Model class keeps score of all measured data and files
    A model consists of an arbitrary number of projects,"""

    def __init__(self) -> None:
        self.current_project: Project = None
        self.projects: List[Project] = list()

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
        """inserts datapoints according to their paths to the current project"""
        for data_point in data_points:
            cfile: CFile = self.current_project.get_cfile(data_point.path)
            cfile.data_entries.append(data_point)

    def add_project(self, project: Project) -> None:
        """adds new project to model"""
        self.projects.append(project)
        self.current_project = project
