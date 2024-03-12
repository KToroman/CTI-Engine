import multiprocessing
from multiprocessing.synchronize import Event as SyncEvent
import threading
from multiprocessing import Queue

from src.builder.BuilderInterface import BuilderInterface
from src.builder.header_builder.CompilingTool import CompilingTool
from src.model.core.SourceFile import SourceFile


class BuilderThread:
    def __init__(self, start_building_event: SyncEvent,
            compiling_tool: BuilderInterface, grep_command_queue: Queue, finished_event: SyncEvent) -> None:
        self.__building_event: SyncEvent = start_building_event
        self.__shutdown_event: SyncEvent = multiprocessing.Event()
        self.__compiling_tool: BuilderInterface = compiling_tool
        self.__grep_command_queue: Queue = grep_command_queue
        self.__finished_event: SyncEvent = finished_event

        self.__thread: threading.Thread

    def __run(self) -> None:
        while not self.__shutdown_event.is_set():
            if self.__building_event.is_set():
                self.__add_grep_command_to_queue()
                finished: bool = not self.__compiling_tool.build()
                if finished:
                    self.__finished_event.set()
                else:
                    self.__finished_event.clear()
                self.__building_event.clear()

    def __add_grep_command_to_queue(self):
        header: str = self.__compiling_tool.get_next_header().get_name()
        command: str = 'ps -e | grep ' + header
        self.__grep_command_queue.put(command)


    def start(self) -> None:
        self.__thread = threading.Thread(target=self.__run)
        self.__thread.start()
        print("[Builder Thread]     started.")

    def stop(self) -> None:
        self.__shutdown_event.set()
        if self.__thread.is_alive():
            self.__thread.join()
        print("[Builder Thread]     stopped")
