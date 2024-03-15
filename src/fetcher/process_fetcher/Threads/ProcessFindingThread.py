import os
from multiprocessing import Queue
import subprocess
import time
from re import split
from threading import Thread
from multiprocessing import Lock
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock


from typing import Optional, List

import psutil
from psutil import NoSuchProcess, AccessDenied

from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from multiprocessing.synchronize import Event as SyncEvent


class ProcessFindingThread:
    __STANDARD_GREP_COMMAND: str = 'ps -e | grep cc1plus'

    def __init__(self, shut_down_event: SyncEvent, process_collector_list: list[ProcessCollectorThread],
                 active_event: SyncEvent, active_fetching: bool):
        self.__thread: Thread
        self.__shutdown: SyncEvent = shut_down_event
        self.__work_lock = Lock()
        self.__work: bool = False
        self.__active_fetching = active_fetching
        self.__process_collector_list = process_collector_list
        self.__counter = 0
        self.__finding_list: list[str] = list()
        self.__grep_command: str = self.__STANDARD_GREP_COMMAND
        self.__time_last_found = time.time()
        self.__active_event = active_event

        self.__pid_list: List[str] = list()
        self.__pid_list_lock: SyncLock = Lock()

    def __run(self):
        while self.__active_event.is_set() and (not self.__shutdown.is_set()):
            self.__fetch_process()

        self.__finding_list.clear()

    def start(self):
        print("[ProcessFindingThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
        print("[ProcessFindingThread]    stopped")

    def set_work(self, pid_list: Optional[List[str]]):
        with self.__pid_list_lock:
            if pid_list is not None:
                self.__pid_list.extend(pid_list)

    def __fetch_process(self):
        grep = subprocess.Popen(self.__grep_command, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        temp_counter = 0
        if grep is None:
            return
        for line in grep.stdout:
            with self.__pid_list_lock:
                for pid in self.__pid_list:
                    if pid in line:
                        continue

            temp_counter += 1
            line.strip()
            proc_id = ""
            proc_info = split(" ", line, 10)
            for i in range(proc_info.__len__() - 1):
                if proc_info[i]:
                    proc_id = proc_info[i]
                    break
            try:
                process = psutil.Process(int(proc_id))
                if not self.__active_fetching:
                    if os.getcwd().split("/")[-1] in process.cwd():
                        continue

                if not any(proc_id in l for l in self.__finding_list):
                    time.sleep(0.01)
                    self.__process_collector_list[self.__counter % self.__process_collector_list.__len__()].add_work(
                        process)
                    self.__finding_list.append(proc_id)
                    self.__counter += 1
            except NoSuchProcess:
                continue
            except AccessDenied:
                continue
            except FileNotFoundError:
                continue
        grep.stdout.close()
        if temp_counter == 0 and self.__finding_list.__len__() != 0 or self.__finding_list.__len__() > 50:
            self.__finding_list.clear()
        with self.__pid_list_lock:
            if self.__pid_list.__len__() > 50:
                del self.__pid_list[0 - 10]
