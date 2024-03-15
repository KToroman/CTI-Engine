import os
import time
from datetime import date
from multiprocessing import Queue, Lock
from os.path import join
from threading import Thread
from multiprocessing.synchronize import Lock as SyncLock

from multiprocessing.synchronize import Event as SyncEvent
import psutil
from PyQt5.QtCore import pyqtSignal

from psutil import NoSuchProcess, AccessDenied

from src.fetcher.process_fetcher.Threads.PassiveDataCollectionThread import PassiveDataCollectionThread
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.ProjectFinishedSemaphore import ProjectFinishedSemaphore


class ProcessCollectorThread:
    def __init__(self, process_list: list[psutil.Process], process_list_lock: SyncLock, model: Model,
                 model_lock: SyncLock,
                 check_for_project: bool, fetcher_list: list[PassiveDataCollectionThread], saver_queue: Queue,
                 hierarchy_queue: Queue, save_path: str, shutdown: SyncEvent, project_queue: Queue,
                 finished_event: pyqtSignal, project_finished_event: SyncEvent, active_event: SyncEvent):
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
        self.current_project: str = ""

    def __run(self):
        while self.__active_event.is_set() and (not self.__shutdown.is_set()):
            with self.__work_queue_lock:
                if self.__work_queue:
                    process = self.__work_queue.pop()
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
        with self.__work_queue_lock:
            self.__work_queue.clear()

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
        # process = self.__create_processes(line)
        if process is not None and not self.__is_process_in_list(process):

            project_name = self.__get_project_name(process)

            if self.__check_for_project:
                self.__project_checker(project_name)
            else:
                with self.__model_lock:
                    name = self.__model.get_current_project_name()
                self.__saver_queue.put(name)
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

    def __get_project_name(self, process: psutil.Process) -> str:
        working_dir: str = process.cwd()

        if working_dir.split("build/").__len__() > 1:
            working_dir_split: list[str] = working_dir.split("build/")
            dir_path: str = working_dir_split[0]
            for i in range(working_dir_split.__len__() - 2):
                dir_path = join(dir_path, "build", working_dir_split[i + 1])
            return dir_path

        return working_dir.split("build")[0]

    def __project_checker(self, project_name: str):
        try:
            if self.current_project == project_name:
                return

            with self.__model_lock:
                if (project_name != self.__model.get_current_working_directory() or
                        not self.__model.project_in_semaphore_list(project_name)):
                    if self.__model.current_project is not None and self.__model.project_in_semaphore_list(
                            self.__model.get_current_working_directory()):
                        with self.__model.get_semaphore_by_name(self.__model.current_project.name).set_lock:
                            self.__model.get_semaphore_by_name(
                                self.__model.current_project.name).new_project_set()

                    name = self.__create_project_name(project_name)
                    semaphore: ProjectFinishedSemaphore = ProjectFinishedSemaphore(project_name, name,
                                                                                   self.__project_queue,
                                                                                   self.__finished_event,
                                                                                   self.__project_finished_event,
                                                                                   self.__model.semaphore_list)
                    project = Project(project_name, name)
                    self.__model.add_project(project, semaphore)
                    self.__hierarchy_queue.put(project)
                    self.__saver_queue.put(name)
                else:

                    return
            time.sleep(0.05)
            with self.__model_lock:
                if self.__model.projects.__len__() > 1:
                    print("saving...")
                    self.__saver_queue.put(self.__model.projects[-2].name)
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
