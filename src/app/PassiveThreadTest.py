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
        self.__passive_data_fetcher: FetcherInterface = PassiveDataFetcher(self.__model, "")
        self.__passive_fetch_finished: bool = False
        self.__is_fetching_passive_data: bool = False
        self.is_running = True
        self.saver: SaveToJSON = SaveToJSON()

    def __fetch_passive_data(self):
        while not self.__passive_fetch_finished:
            self.__is_fetching_passive_data = self.__passive_data_fetcher.update_project()

            time.sleep(0.001)

        self.__model.save_project = self.__model.current_project
        self.__is_fetching_passive_data = False
        self.__passive_fetch_finished = True

    def save_project(self):
        local_saver = SaveToJSON()
        while self.is_running:
            tmep_pro = self.__model.get_current_project()
            if tmep_pro is not None:
                local_saver.save_project(tmep_pro)
                time.sleep(0.4)
        local_saver.save_project(self.__model.get_current_project())
        print("saver closed")


    def stop_programm(self):
        input("press button \n")
        self.is_running = False
        self.__passive_fetch_finished = True

    def main_loop(self):
        start = time.time()
        Thread(target=self.stop_programm).start()
        Thread(target=self.__fetch_passive_data).start()
        Thread(target=self.save_project).start()
        while self.is_running:
            time.sleep(5)
            print(self.__is_fetching_passive_data.__str__())

        time.sleep(1)
        print("fin in time: " + (time.time() - start).__str__())

    def length(self):
        counter = 0
        print("Project Count: " + self.__model.projects.__len__().__str__())
        for p in self.__model.projects:
            print(
                '\n' + "workind_dir: " + p.working_dir + ". project_pid: " + p.origin_pid.__str__() +
                ". SoureFiles_count: " + p.source_files.__len__().__str__())
            counter += 1
            conter = 0
            for c in p.source_files:
                conter += 1
                print("       " + c.path + ": " + c.data_entries.__len__().__str__())
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
