import subprocess
import time
from re import split
from threading import Event, Thread, Lock
from typing import List
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread


class ProcessFindingThread:
    def __init__(self, process_collector_list: List[ProcessCollectorThread]):
        self.__thread: Thread = None
        self.__shutdown: Event = Event()
        self.__shutdown.clear()
        self.__work_lock = Lock()
        self.__work: bool = False
        self.__process_collector_list = process_collector_list
        self.__counter = 0
        self.__finding_list: List[str] = list()

    def __run(self):
        while not self.__shutdown.is_set():
            if self.has_work():
                self.__fetch_process()
                with self.__work_lock:
                    self.__work = False

    def start(self):
        print("[ProcessFindingThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        print("[ProcessFindingThread]    stopped")
        self.__shutdown.set()
        self.__thread.join()

    def has_work(self) -> bool:
        with self.__work_lock:
            return self.__work

    def set_work(self):
        if not self.has_work():
            with self.__work_lock:
                self.__work = True

    def __fetch_process(self):
        grep = subprocess.Popen('ps -e | grep cc1plus', stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        temp_counter = 0
        for line in grep.stdout:
            temp_counter += 1
            proc_id = ""
            proc_info = split(" ", line, 10)
            for i in range(proc_info.__len__() - 1):
                if proc_info[i]:
                    proc_id = proc_info[i]
                    break
            if not any(proc_id in l for l in self.__finding_list):
                self.__process_collector_list[self.__counter % self.__process_collector_list.__len__()].add_work(line)
                self.__finding_list.append(proc_id)
                self.__counter += 1
        grep.stdout.close()
        if temp_counter == 0 and self.__finding_list.__len__() != 0:
            self.__finding_list.clear()
