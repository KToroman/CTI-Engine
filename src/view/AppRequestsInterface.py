from multiprocessing import Event, Queue
from typing import Protocol

'''An interface for passing requests to the App'''
class AppRequestsInterface(Protocol):
    # Events for gui
    shutdown_event = Event()
    active_mode_event = Event()
    passive_mode_event = Event()
    passive_mode_event.set()
    load_event = Event()

    # Queues for gui messages
    load_path_queue: Queue = Queue(1)
    active_mode_queue: Queue = Queue(1)
    error_queue: Queue = Queue(5)
