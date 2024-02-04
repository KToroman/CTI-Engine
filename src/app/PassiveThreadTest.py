import copy
from enum import Flag
import time
from threading import Thread
from typing import List

from src.fetcher.FetcherInterface import (FetcherInterface)
from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.saving.SaveToJSON import SaveToJSON


class PassiveThread:

    def __init__(self):
        self.__model: Model = Model()
        self.__passive_thread = None
        self.__passive_data_fetcher: FetcherInterface = PassiveDataFetcher(
            self.__model, "")
        self.__passive_fetch_finished: bool = False
        self.__is_fetching_passive_data: bool = False
        self.is_running = True
        self.saver: SaveToJSON = SaveToJSON()
        self.is_saved_bool = False


    def __fetch_passive_data(self):
        project_time = time.time() + 5

        while not self.__passive_fetch_finished:
            self.__is_fetching_passive_data = self.__passive_data_fetcher.update_project()
            time.sleep(0.0001)
            # metrics_ram: Metric = Metric(12, MetricName.RAM)
            # metrics_cpu: Metric = Metric(16, MetricName.CPU)
            # metr_list: List[Metric] = [metrics_ram, metrics_cpu]
            # entrys: List[DataEntry] = [
            #     DataEntry("sourcefile" + (time.time()/10
            #                               ).__int__().__str__(), time.time(), metr_list)]
            # self.__model.insert_datapoints(entrys)
            # if project_time <= time.time():
            #     self.__model.add_project(Project("", time.time().__int__(), ""))
            #     project_time = time.time() + 600
            #     print("new Project")

            # self.__is_fetching_passive_data = True
        self.__model.save_project = self.__model.current_project
        self.__is_fetching_passive_data = False
        self.__passive_fetch_finished = True
        self.is_saved_bool = False

    def save(self):
        self.__model.time_left = time.time() + 1
        time_to_save = time.time() + 3
        while self.is_running or not self.is_saved_bool:
            if time_to_save <= time.time() and self.__model.save_project is not None:
                self.__model.update_save_project()
                time_to_save = time.time() + 3
                self.saver.save_project(self.__model.get_current_project())
                print(self.__model.get_current_project().origin_pid)
                self.is_saved_bool = True
                print("Saved")

    def stop_programm(self):
        input("press button \n")
        self.is_running = False
        self.__passive_fetch_finished = True

    def main_loop(self):
        start = time.time()
        t1 = Thread(target=self.stop_programm)
        self.__passive_thread = Thread(target=self.__fetch_passive_data)
        t1.start()
        self.__passive_thread.start()
        sver_t = Thread(target=self.save)
        sver_t.start()
        while self.is_running:
            pass

        time.sleep(1)
        print("fin in time: " + (time.time()-start).__str__())

    def length(self):
        counter = 0
        print("Project Count: " + self.__model.projects.__len__().__str__())
        for p in self.__model.projects:
            print(p.origin_pid.__str__() + ": " +
                  p.source_files.__len__().__str__())
            counter += 1
            for c in p.source_files:
                print(p.origin_pid.__str__() + " " + c.path +
                      ": " + c.data_entries.__len__().__str__())
                counter += 1 + c.data_entries.__len__()

        print("insgesamt: " + counter.__str__())


p = PassiveThread()

p.main_loop()

time.sleep(1)
p.length()

"""
m = Model()

loader = FileLoader("C:\\Users\\cashe\\git\\cti-engine-prototype\\saves\\CTI_ENGINE_SAVE 69 1706829466", m)
loader.update_project()

e_loader = FileLoader("C:\\Users\\cashe\\git\\cti-engine-prototype\\saves\\CTI_ENGINE_SAVE 1706829468 1706829471", m)
e_loader.update_project()

p_e_loader = FileLoader("C:\\Users\\cashe\\git\\cti-engine-prototype\\saves\\CTI_ENGINE_SAVE 1706829498 1706829501", m)
p_e_loader.update_project()

p_e_cloader = FileLoader("C:\\Users\\cashe\\git\\cti-engine-prototype\\saves\\CTI_ENGINE_SAVE 1706829528 1706829531", m)
p_e_cloader.update_project()

print("Project Count: " + m.projects.__len__().__str__() )
for p in m.projects:
    print(p.origin_pid.__str__() + ": " + p.source_files.__len__().__str__()) """
