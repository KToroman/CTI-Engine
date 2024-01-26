from typing import List

from ModelReadViewInterface import ModelReadViewInterface
from model.core.CFile import CFile
from model.core.CFileReadViewInterface import CFileReadViewInterface
from core.DataEntry import DataEntry
from core.Project import Project
from model.core.FileDictionary import FileDictionary


class Model(ModelReadViewInterface):
    '''
Model class keeps score of all measured data and files
A model consists of an arbitrary number of projects,
'''
    def __init__(self):
        self.current_project = None
        self.projects = list(Project)

    def get_project_name(self) -> str:
        name: str = self.current_project.working_dir + \
            str(self.current_project.origin_pid)
        return name

    def get_cfiles(self) -> list[CFileReadViewInterface]:
        '''returns '''
        cfiles_view: List[CFileReadViewInterface] = list(
            CFileReadViewInterface)
        cfiles_view.extend(self.current_project.source_files)
        return cfiles_view

    def insert_datapoints(self, data_points: list[DataEntry]):
        '''inserts datapoints according to their paths to the current project'''
        for data_point in data_points:
            cfile: CFile = self.current_project.get_cfile(data_point.path)
            cfile.data_entries.append(data_point)

    def add_project(self, project: Project):
        '''adds new project to model'''
        self.projects.append(project)
        self.current_project = project
