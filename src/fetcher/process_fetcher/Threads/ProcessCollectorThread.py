import os
import time
from datetime import date
from multiprocessing import Queue
from os.path import join
from re import split
from threading import Thread
from multiprocessing import Lock
from multiprocessing.synchronize import Event as SyncEvent
import psutil
from PyQt5.QtCore import pyqtSignal
from colorama import Fore
from psutil import NoSuchProcess, AccessDenied
from typing import Optional

from src.fetcher.process_fetcher.Threads.DataCollectionThread import DataCollectionThread
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.ProjectFinishedSemaphore import ProjectFinishedSemaphore


class ProcessCollectorThread:
    def __init__(self, process_list: list[psutil.Process], process_list_lock: Lock, model: Model, model_lock: Lock,
                 check_for_project: bool, fetcher_list: list[DataCollectionThread], saver_queue: Queue,
                 hierarchy_queue: Queue, save_path: str, shutdown: SyncEvent, project_queue: Queue,
                 finished_event: pyqtSignal, project_finished_event: SyncEvent, active_event: SyncEvent,
                 line_work_queue: Queue):
        self.__thread: Thread
        self.__shutdown = shutdown
        self.__work_queue_lock = Lock()
        self.__work_queue: list[psutil.Process] = list()
        self.__process_list = process_list
        self.__process_list_lock = process_list_lock
        self.__model = model
        self.__model_lock = model_lock
        self.__check_for_project = check_for_project
        self.__fetcher = fetcher_list
        self.__save_path = save_path
        self.__not_fetched: list[psutil.Process] = list()
        self.__saver_queue = saver_queue
        self.__hierarchy_queue = hierarchy_queue
        self.__counter = 0
        self.time_till_false: float = 0
        self.__active_event = active_event

        self.__project_queue = project_queue
        self.__finished_event = finished_event
        self.__project_finished_event = project_finished_event
        self.__line_work_queue = line_work_queue

    def __run(self):
        while not self.__shutdown.is_set():
            #if not self.__active_event.is_set():
            #    with self.__work_queue_lock:
            #       self.__work_queue.clear()
            #    continue
            #

            with self.__work_queue_lock:
                if self.__work_queue:
            #if not self.__line_work_queue.empty():
                    process = self.__work_queue.pop()
                #print(self.__work_queue.__len__())
                #process = self.__line_work_queue.get()
                else:
                    continue

            try:
                self.__make_process(process)
            except AccessDenied:
                continue
            except NoSuchProcess:
                continue
            except ValueError:
                continue

    def start(self):
        print("[ProcessCollectorThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
        print("[ProcessCollectorThread]    stopped now")

    def add_work(self, process: psutil.Process):
        time.sleep(0.01)
        with self.__work_queue_lock:
            self.__work_queue.append(process)

    def __make_process(self, process: psutil.Process):
        #process = self.__create_processes(line)
        if process is not None and not self.__is_process_in_list(process):
            if self.__check_for_project:
                pass

            project_name = self.__get_project_name(process)
            if project_name == "del":
                return
            self.__project_checker(project_name)
            self.__counter += 1
            self.time_till_false = time.time() + 45
            with self.__process_list_lock:
                self.__process_list.append(process)
            if not self.__fetcher[self.__counter % len(self.__fetcher)].has_work():
                self.__fetcher[self.__counter % len(self.__fetcher)].add_work(process)
            else:
                for f in self.__fetcher:
                    if not f.has_work():
                        f.add_work(process)
                        break

    def __create_processes(self, line: str) -> Optional[psutil.Process]:
        line.strip()
        proc_info = split(" ", line, 10)
        proc_id = proc_info[0]
        process = psutil.Process(int(proc_id))
        return process

    def __get_project_name(self, process: psutil.Process) -> str:
        working_dir: str = process.cwd()
        if os.getcwd().split("/")[-1] in working_dir:
            return "del"

        if working_dir.split("build/").__len__() > 1:
            working_dir_split: list[str] = working_dir.split("build/")
            dir_path: str = working_dir_split[0]
            for i in range(working_dir_split.__len__() - 2):
                dir_path = join(dir_path, "build", working_dir_split[i + 1])
            return dir_path

        return working_dir.split("build")[0]

    def __project_checker(self, project_name: str):
        try:
            time.sleep(0.01)
            with self.__model_lock:
                if (project_name != self.__model.get_current_working_directory() or
                        not self.__model.project_in_semaphore_list(project_name)):
                    if self.__model.current_project is not None and self.__model.project_in_semaphore_list(
                            self.__model.get_current_working_directory()):
                        with self.__model.get_semaphore_by_name(self.__model.get_current_working_directory()).set_lock:
                            self.__model.get_semaphore_by_name(
                                self.__model.get_current_working_directory()).new_project_set()

                    name = self.__create_project_name(project_name)
                    semaphore: ProjectFinishedSemaphore = ProjectFinishedSemaphore(project_name, name,
                                                                                   self.__project_queue,
                                                                                   self.__finished_event,
                                                                                   self.__project_finished_event,
                                                                                   self.__model.semaphore_list)
                    self.__model.add_project(Project(project_name, name), semaphore)
                    self.__hierarchy_queue.put(name)
                    self.__saver_queue.put(name)
        except NoSuchProcess:
            return

    def __is_process_in_list(self, process: psutil.Process) -> bool:
        time.sleep(0.01)
        with self.__process_list_lock:
            for proc in self.__process_list:
                try:
                    if proc.pid == process.pid:
                        return True
                except NoSuchProcess:
                    continue
            return False

    def __create_project_name(self, project_name: str) -> str:
        time_date = date.today()
        project_name_split = project_name.split("/")
        name = project_name_split[- 1]
        if name is None or name == "":
            name = project_name_split[- 2]

        name = (name + "_" + time_date.__str__())
        if os.path.exists(join(self.__save_path, name)):
            for i in range(1, 10):
                name_temp = f"{name}_{i}"
                if not os.path.exists(join(self.__save_path, name_temp)):
                    return name_temp

            name = f"{name}_{int(time.time())}"
            return name

        return name
