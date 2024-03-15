from threading import Thread
import time
from multiprocessing.synchronize import Event as SyncEvent

from PyQt5.QtCore import pyqtSignal

from multiprocessing import Queue

from src.model.core.StatusSettings import StatusSettings


class GUICommunicationManager:
    def __init__(self, shutdown_event: SyncEvent, error_queue: Queue, error_signal: pyqtSignal, passive_mode_event: SyncEvent,
                 status_queue: Queue, status_signal: pyqtSignal, fetching_passive_data: SyncEvent,
                 active_measurement_active: SyncEvent, finished_project_event: SyncEvent,
                 load_event: SyncEvent, cancel_event: SyncEvent, restart_event: SyncEvent, hierarchy_fetching_event: SyncEvent,
                 fetching_hierarchy: SyncEvent):
        self.__error_queue = error_queue
        self.__error_signal = error_signal
        self.__status_signal: pyqtSignal = status_signal
        self.__status_queue: Queue = status_queue
        self.__shutdown_event: SyncEvent = shutdown_event
        self.__thread: Thread
        self.__status: StatusSettings = StatusSettings.SEARCHING
        self.__time_of_last_status_change: float = -5
        self.__cancel_event = cancel_event
        self.__passive_mode_event: SyncEvent = passive_mode_event
        self.__active_measurement_active: SyncEvent = active_measurement_active
        self.__found_project: SyncEvent = fetching_passive_data
        self.__finished_project_event: SyncEvent = finished_project_event
        self.__load_event: SyncEvent = load_event
        self.__restart_event = restart_event
        self.__hierarchy_fetching_event = hierarchy_fetching_event
        self.__fetching_hierarchy = fetching_hierarchy

    def start(self):
        print("[StatusAndErrorThread]   started.")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self):
        while not self.__shutdown_event.is_set():
            if not self.__error_queue.empty():
                self.__deploy_error()

            if self.__cancel_event.is_set():
                self.__cancel_event.clear()
                if self.__passive_mode_event.is_set() or self.__active_measurement_active.is_set():
                    self.__cancel_event.clear()
                    self.__status = StatusSettings.CANCELLED
                    self.__time_of_last_status_change = time.time() + 1.5
                    self.__deploy_status()
                self.__passive_mode_event.clear()
                self.__hierarchy_fetching_event.clear()
                self.__active_measurement_active.clear()

            if self.__load_event.is_set():
                self.__cancel_event.set()
                self.__status = StatusSettings.LOADING
                self.__time_of_last_status_change = time.time() + 1.5
                self.__deploy_status()
                self.__passive_mode_event.clear()
                self.__hierarchy_fetching_event.clear()
                self.__active_measurement_active.clear()

            if self.__restart_event.is_set():
                self.__restart_event.clear()
                self.__passive_mode_event.set()
                self.__hierarchy_fetching_event.set()
                self.__time_of_last_status_change = 0
            deploy_status_now: bool = self.__update_status()
            if deploy_status_now:
                self.__deploy_status()
            self.__deploy_error()

    def __deploy_error(self):
        if not self.__error_queue.empty():
            self.__error_signal.emit()

    def __update_status(self) -> bool:
        if self.__time_of_last_status_change + 1.5 > time.time():
            return False
        self.__status = StatusSettings.WAITING
        if self.__cancel_event.is_set():
            self.__status = StatusSettings.CANCELLED
        if self.__passive_mode_event.is_set():
            self.__status = StatusSettings.SEARCHING
        if self.__found_project.is_set():
            self.__status = StatusSettings.MEASURING
        elif self.__fetching_hierarchy.is_set():
            self.__status = StatusSettings.HIERARCHY
        if self.__finished_project_event.is_set():
            self.__status = StatusSettings.FINISHED
        if self.__active_measurement_active.is_set():
            self.__status = StatusSettings.MEASURING
        if self.__load_event.is_set():
            self.__status = StatusSettings.LOADING
        self.__time_of_last_status_change = time.time()
        return True

    def __deploy_status(self):
        self.__status_queue.put(self.__status)
        self.__status_signal.emit()



    def stop(self):
        self.__thread.join()
        print("[StatusAndErrorThread]   stopped.")
