import os
from multiprocessing import Queue
import subprocess
import time
from re import split
from threading import Thread
from multiprocessing import Lock
from multiprocessing.synchronize import Event as SyncEvent

from typing import Optional, List

import psutil
from psutil import NoSuchProcess

from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from multiprocessing.synchronize import Event as SyncEvent


class ProcessFindingThread:
    __STANDARD_GREP_COMMAND: str = 'ps -e | grep cc1plus'

    def __init__(self, shut_down_event: SyncEvent, process_collector_list: list[ProcessCollectorThread],
                 active_event: SyncEvent, line_work_queue: Queue):
        self.__thread: Thread
        self.__shutdown: SyncEvent = shut_down_event
        self.__work_lock = Lock()
        self.__work: bool = False
        self.__process_collector_list = process_collector_list
        self.__counter = 0
        self.__finding_list: list[str] = list()
        self.__grep_command: str = self.__STANDARD_GREP_COMMAND
        self.__time_last_found = time.time()
        self.__active_event = active_event
        self.__line_work_queue = line_work_queue

    def __run(self):
        while not self.__shutdown.is_set():
            #if not self.__active_event.is_set():
             #   self.__finding_list.clear()
              #  continue
            if self.has_work():
                self.__fetch_process()
                with self.__work_lock:
                    self.__work = False

    def start(self):
        print("[ProcessFindingThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
        print("[ProcessFindingThread]    stopped")

    def has_work(self) -> bool:
        with self.__work_lock:
            return self.__work

    def set_work(self):
        if not self.has_work():
            with self.__work_lock:
                self.__work = True

    def __fetch_process(self):

        grep = subprocess.Popen(self.__grep_command, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        temp_counter = 0
        if grep == None:
            return
        for line in grep.stdout:
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
                if not any(proc_id in l for l in self.__finding_list) and not os.getcwd().split("/")[-1] in process.cwd():
                    time.sleep(0.01)
                    self.__process_collector_list[self.__counter % self.__process_collector_list.__len__()].add_work(process)
                    #self.__line_work_queue.put(process)
                    self.__finding_list.append(proc_id)
                    self.__counter += 1
            except NoSuchProcess:
                continue
        grep.stdout.close()
        if temp_counter == 0 and self.__finding_list.__len__() != 0 or self.__finding_list.__len__() > 50:
            self.__finding_list.clear()



