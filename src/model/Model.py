from ModelReadViewInterface import ModelReadViewInterface
from model.core.CFileReadViewInterface import CFileReadViewInterface
from core.DataEntry import DataEntry
from core.Project import Project

'''
Model class keeps score of all measured data and files
A model consists of an arbitrary number of projects,
'''
class Model(ModelReadViewInterface):
    def __init__(self):
        self.current_project = None
        self.projects = list(Project)

    def get_project_name(self) -> str:
        name: str = self.current_project.working_dir + str(self.current_project.origin_pid)
        return name

    def get_cfiles(self) -> list[CFileReadViewInterface]:
        cfiles_view: list[CFileReadViewInterface] = list(CFileReadViewInterface)
        cfiles_view.extend(self.current_project.source_files)
        return cfiles_view

    def insert_datapoints(data_points: list[DataEntry]):
        for data_point in data_point:
            pass
            # I think all the CFiles need to be in a map
            # else, we'll have to iterate trough each file to find the 
            # corresponding object to each datapoint
        raise NotImplementedError
    
    '''adds new project to model'''
    def add_project(self, project: Project):
        self.projects.append(project)
        self.current_project = project