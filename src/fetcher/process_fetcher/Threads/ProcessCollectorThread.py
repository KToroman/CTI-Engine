import os
import time
from datetime import date
from multiprocessing import Queue
from os.path import join
from re import split
from threading import Event, Thread, Lock
from typing import List, Optional, IO

import psutil
from psutil import NoSuchProcess, AccessDenied

from src.fetcher.process_fetcher.Threads.FetcherThread import FetcherThread
from src.model.Model import Model
from src.model.core.Project import Project


class ProcessCollectorThread:
    def __init__(self, process_list: List[psutil.Process], process_list_lock: Lock, model: Model, model_lock: Lock,
                 check_for_project: bool, fetcher_list: List[FetcherThread], saver_queue: Queue,
                 hierarchy_queue: Queue, save_path: str, shutdown: Event):
        self.__thread: Thread
        self.__shutdown = shutdown
        self.__work_queue_lock = Lock()
        self.__work_queue: List[str] = list()
        self.__process_list = process_list
        self.__process_list_lock = process_list_lock
        self.__model = model
        self.__model_lock = model_lock
        self.__check_for_project = check_for_project
        self.__fetcher = fetcher_list
        self.__save_path = save_path
        self.__not_fetched: List[psutil.Process] = list()
        self.__saver_queue = saver_queue
        self.__hierarchy_queue = hierarchy_queue
        self.__counter = 0
        self.time_till_false: float = 0

    def __run(self):
        while not self.__shutdown.is_set():
            time.sleep(0.001)
            line = ""
            with self.__work_queue_lock:
                if self.__work_queue.__len__() != 0:
                    line = self.__work_queue.pop()
            try:
                if line != "":
                    self.__make_process(line)
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

    def add_work(self, line: str):
        time.sleep(0.001)
        with self.__work_queue_lock:
            proc_id = ""
            proc_info = split(" ", line, 10)
            for i in range(proc_info.__len__() - 1):
                if proc_info[i]:
                    proc_id = proc_info[i]
                    break
            if not any(proc_id in l for l in self.__work_queue):
                self.__work_queue.append(line)

    def __make_process(self, line: str):
        process = self.__create_processes(line)
        if process is not None and not self.__is_process_in_list(process):
            if self.__check_for_project:

                project_name = self.__get_project_name(process)
                if project_name == "del":
                    return
                self.__project_checker(project_name)
            with self.__process_list_lock:
                self.__process_list.append(process)
            if not self.__fetcher[self.__counter % len(self.__fetcher)].has_work():
                self.__fetcher[self.__counter % len(self.__fetcher)].add_work(process)
            else:
                for f in self.__fetcher:
                    if not f.has_work():
                        f.add_work(process)
                        break
            self.time_till_false = time.time() + 15

    def __create_processes(self, line: str) -> Optional[psutil.Process]:
        proc_id = ""
        proc_info = split(" ", line, 10)
        for i in range(proc_info.__len__() - 1):
            if proc_info[i]:
                proc_id = proc_info[i]
                break
        process = psutil.Process(int(proc_id))
        return process

    def __get_project_name(self, process: psutil.Process) -> str:
        working_dir: str = process.cwd()
        if os.getcwd().split("/")[-1] in working_dir:
            return "del"

        if working_dir.split("build/").__len__() > 1:
            working_dir_split: List[str] = working_dir.split("build/")
            dir_path: str = working_dir_split[0]
            for i in range(working_dir_split.__len__() - 2):
                dir_path = join(dir_path, "build", working_dir_split[i+1])
            return dir_path

        return working_dir.split("build")[0]

    def __project_checker(self, project_name: str):
        try:
            with self.__model_lock:
                if project_name != self.__model.get_current_working_directory():
                    self.__model.add_project(Project(project_name, self.__create_project_name(project_name)))
                    self.__hierarchy_queue.put(project_name)
                    self.__saver_queue.put(project_name)
        except NoSuchProcess:
            return

    def __is_process_in_list(self, process: psutil.Process) -> bool:
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

        name = (name + " " + time_date.__str__())
        if os.path.exists(join(self.__save_path, name)):
            for i in range(1, 10):
                name = f"{name} {i}"
                if os.path.exists(join(self.__save_path, name)):
                    return name

            name = f"{name} {time.time()}"
            return name

