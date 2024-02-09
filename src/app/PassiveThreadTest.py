import multiprocessing
import time
from threading import Thread
from typing import List

from src.fetcher.FetcherInterface import (FetcherInterface)
from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.model.Model import Model
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface
from src.saving.SaveToJSON import SaveToJSON
from multiprocessing import Process


class PassiveThread:

    def __init__(self):
        self.__cancel_measurement: bool = False
        self.__model: Model = Model()
        self.__hierarchy: FetcherInterface = HierarchyFetcher(self.__model)
        self.__passive_data_fetcher: FetcherInterface = PassiveDataFetcher(self.__model)

        self.__is_measuring: bool = False
        self.is_running = True
        self.saver: SaveToJSON = SaveToJSON()

    def __passive_measurement(self):
        curr_project_name: str
        curr_project_name = self.__model.get_current_working_directory()
        Process(target=self.passsss).start()
        while not self.__cancel_measurement:
            if curr_project_name != self.__model.get_current_working_directory():
                Thread(target=self.__make_hierarchy).start()
                curr_project_name = self.__model.get_current_working_directory()
                Thread(target=self.__save_project, args=[curr_project_name]).start()
            time.sleep(0.01)
        self.__running_passive_fetcher = False

    def passsss(self):
        while not self.__cancel_measurement:
            self.__is_measuring = self.__passive_data_fetcher.update_project()

    def __make_hierarchy(self):
        try:
            time.sleep(2)
            hier_bool = True
            while hier_bool:
                time.sleep(3)
                hier_bool = self.__hierarchy.update_project()
        except:
            print("Hierarchy err")

    def __save_project(self, name: str):
        saver: SaveInterface = SaveToJSON()
        stop_time: float = time.time() + 10
        print("saver opend")
        while stop_time > time.time() and not self.__cancel_measurement:
            project = self.__model.get_project_by_name(name)
            saver.save_project(project)
            time.sleep(3)
            if project.working_dir == self.__model.get_current_project().working_dir:
                stop_time = time.time() + 10
        saver.save_project(self.__model.get_project_by_name(name))
        print("saver colsed")

    def stop_programm(self):
        input("press button \n")
        self.is_running = False
        self.__cancel_measurement = True

    def main_loop(self):
        start = time.time()
        Thread(target=self.stop_programm, daemon=True).start()
        Thread(target=self.__passive_measurement).start()
        while self.is_running:
            time.sleep(5)
            print(self.__is_measuring.__str__())

        time.sleep(1)
        print("fin in time: " + (time.time() - start).__str__())

    def get_header_count(self, source_file: CFileReadViewInterface, counter: int) -> int:
        if not source_file.get_headers():
            return counter
        for header in source_file.get_headers():
            counter += 1
            return self.get_header_count(header, counter)

    def set_model(self, model: Model):
        self.__model = model

    def length(self):
        counter = 0
        print("Project Count: " + self.__model.projects.__len__().__str__())
        for p in self.__model.projects:
            print(
                '\n' + "workind_dir: " + p.working_dir + ". project_pid: " +
                ". SoureFiles_count: " + p.source_files.__len__().__str__())
            counter += 1
            conter = 0
            for c in p.source_files:
                counter = self.get_header_count(c, counter)
                conter += 1
                print("       " + c.path + ": " + c.data_entries.__len__().__str__())
                counter += 1 + c.data_entries.__len__()

        print("insgesamt: " + counter.__str__())

"""
if __name__ == '__main__':
    p = PassiveThread()

    p.main_loop()

    time.sleep(1)
    p.length()
"""


def length(p: Project):
    counter_has_entry = 0
    counter_has_none = 0
    for c in p.source_files:
        if c.data_entries.__len__() > 1:
            counter_has_entry += 1
        else:
            counter_has_none += 1

    print(f" has found {counter_has_entry} CFiles with entrys, and {counter_has_none} without")


p = PassiveThread()

m = Model()

loader = FileLoader(
    "/common/homes/students/uvhuj_heusinger/Documents/git/cti-engine-prototype/saves/deps/opencv-3/main/opencv-3.4.16/1707483711.1979697/CTI_ENGINE_SAVE opencv-3.4.16 2024-02-09",
    m)
loader.update_project()
p.set_model(m)
p.length()

length(m.current_project)
