from threading import Event, Thread
import time

from PyQt5.QtCore import pyqtSignal

from multiprocessing import Queue

from src.model.core.StatusSettings import StatusSettings


class StatusAndErrorThread:
    def __init__(self, shutdown_event: Event, error_queue: Queue, error_signal: pyqtSignal, passive_mode_event:Event, 
                 status_queue: Queue, status_signal: pyqtSignal, fetching_passive_data: Event, active_measurement_active: Event, finished_project_event: Event, 
                 load_event: Event):
        self.__error_queue: Queue = error_queue
        self.__error_signal: pyqtSignal = error_signal
        self.__status_signal: pyqtSignal = status_signal
        self.__status_queue: Queue = status_queue
        self.__shutdown_event: Event = shutdown_event
        self.__thread: Thread
        self.__status: StatusSettings = StatusSettings.SEARCHING
        self.__time_of_last_status_change: float = -5

        self.__passive_mode_event: Event = passive_mode_event
        self.__active_measurement_active: Event = active_measurement_active
        self.__found_project: Event = fetching_passive_data
        self.__finished_project_event: Event = finished_project_event
        self.__load_event: Event = load_event

    def start(self):
        print("[StatusAndErrorThread]   started.")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self):
        while not self.__shutdown_event.is_set():
            if not self.__error_queue.empty():
                self.__deploy_error()
            deploy_status_now: bool = self.__update_status()
            if (deploy_status_now):
                self.__deploy_status()

    def __deploy_error(self):
        error: BaseException = self.__error_queue.get(True, 7)
        if (error == None):
            return
        self.__error_signal.emit()

    def __update_status(self) -> bool:
        if (self.__time_of_last_status_change + 3 > time.time()):
            return False
        self.__status = StatusSettings.WAITING
        if (self.__passive_mode_event.is_set()):
            self.__status = StatusSettings.SEARCHING
        if (self.__found_project.is_set()):
            self.__status = StatusSettings.MEASURING
        if (self.__finished_project_event.is_set()):
            self.__status = StatusSettings.FINISHED
        if (self.__active_measurement_active.is_set()):
            self.__status = StatusSettings.MEASURING
        if (self.__load_event.is_set()):
            self.__status = StatusSettings.LOADING
        self.__time_of_last_status_change = time.time()
        return True
        
    def __deploy_status(self):
        self.__status_queue.put(self.__status)
        self.__status_signal.emit()

    def stop(self):
        print("[StatusAndErrorThread]   stop signal sent.")