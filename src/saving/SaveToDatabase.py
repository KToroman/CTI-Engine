import time

from rocksdict import Rdict
from pathlib import Path
from typing import List
from multiprocessing.synchronize import Lock as SyncLock

from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model


from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToDatabase(SaveInterface):

    def __init__(self, saves_path: str, model_lock: SyncLock, model: Model):
        print("initializing")
        self.__current_project_name: str = ""
        self.__saves_path_prefix = saves_path
        self.__saves_path: str = saves_path
        print("[SaveToDatabase]     " + self.__saves_path)
        self.__model_lock = model_lock
        self.__model: Model = model

    def save_project(self, project_name: str):
        project = self.__model.get_project_by_name(project_name)
        print("[SaveToDatabase]     found project in model")
        with self.__model_lock:
            print("[SaveToDatabase]     now in modellock")
            delta: List[DataBaseEntry] = project.delta_entries
            project.delta_entries = list()
        if self.__current_project_name != project_name:
            print("[SaveToDataBase]     new project saved")
            self.__add_new_project(project)
            # project is being saved for the first time
        self.__add_to_data_base(delta)
        print(f"[SaveToDatabase]    saved {len(delta)} new entries")

    def __add_new_project(self, project: Project):
        self.__current_project_name = project.name
        self.__saves_path = self.__saves_path_prefix + project.path_to_save
        Path(self.__saves_path).mkdir(exist_ok=True, parents=True)
        db: Rdict = Rdict(self.__saves_path)
        db.close()

    def __add_to_data_base(self, delta: List[DataBaseEntry]):
        db: Rdict = Rdict(self.__saves_path)
        print(f"[SaveToDatabase]    opened Database: {self.__saves_path}")
        for entry in delta:
            if entry.timestamp is None:
                timestamp = time.time()
            else:
                timestamp = entry.timestamp
            key = f"{entry.path}\n{entry.parent_or_compile_command}\n{entry.hierarchy_level}\n{timestamp}"
            if entry.metrics is None:
                value = None
            else:
                value = entry.metrics
                paths = entry.path.split("/")
                print_path = paths[-1]+"/"+paths[-2]+"/"+paths[-3]
                print(f"[SaveToDatabase]    added entry with time: {entry.timestamp}, path:{print_path}")
            db[key] = value
        db.close()
