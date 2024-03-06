import subprocess
import time
from re import split
from threading import Event, Thread, Lock
from typing import List
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread


class ProcessFindingThread:
    def __init__(self, process_collector_list: List[ProcessCollectorThread]):
        self.thread: Thread = None
        self.shutdown: Event = Event()
        self.shutdown.clear()
        self.__work_lock = Lock()
        self.__work: bool = False
        self.__process_collector_list = process_collector_list
        self.counter = 0
        self.finding_list: List[str] = list()

    def collect_data(self):
        while not self.shutdown.is_set():
            if self.has_work():
                self.__fetch_process()
                with self.__work_lock:
                    self.__work = False

    def start(self):
        print("[ProcessFindingThread]    started")
        self.thread = Thread(target=self.collect_data)
        self.thread.start()

    def stop(self):
        print("[ProcessFindingThread]    stopped")
        self.shutdown.set()
        self.thread.join()

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
            if not any(proc_id in l for l in self.finding_list):
                self.__process_collector_list[self.counter % self.__process_collector_list.__len__()].add_work(line)
                self.finding_list.append(proc_id)
                self.counter += 1
        grep.stdout.close()
        if temp_counter == 0 and self.finding_list.__len__() != 0:

            self.finding_list.clear()

