from io import TextIOWrapper
from os.path import join


from pathlib import Path
from typing import List


from src.model.core.CFile import CFile
from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToCSV(SaveInterface):

    def __init__(self, saves_path: str):
        self.__current_project_name: str = ""
        self.__saves_path: Path = Path(saves_path)
        self.__files_needing_updates: List[CFile] = list()

    def save_project(self, project: Project):
        if self.__set_name(project):
            # project is being saved for the first time
            self.__set_path()
        self.__saves_path.mkdir(exist_ok=True, parents=True)
        path_file_collection: str = join(self.__saves_path, "c_files")
        with open(path_file_collection, "w") as file_collection:
            self.update_file_collection(file_collection)
            # see which files have new dataentries:
            # for each file in self.__files_needing_update:
            self.append_data_entries(cfile: CFile)
    
    def update_file_collection(self, file_collection: TextIOWrapper):
        #first: see if there are any new sourcefiles:

        #then: see if any sourcefiles have new headers:

        pass

    def append_data_entries(self, cfile: CFile):
        # append all dataentries > index
        pass


    def __set_name(self, project: Project) -> bool:
        if self.__current_project_name != project.name:
            self.__current_project_name = project.name
            return True
        return False
    
    def __set_path(self):
        path: str = join(self.__saves_path, self.__current_project_name)
        self.__saves_path = Path(path)

