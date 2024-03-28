from multiprocessing import Event, Queue
from multiprocessing.synchronize import Event as SyncEvent
from typing import Protocol


class AppRequestsInterface(Protocol):
    """an interface for passing requests to the App."""

    # Events for GUI
    shutdown_event: SyncEvent = Event()
    active_mode_event: SyncEvent = Event()
    passive_mode_event: SyncEvent = Event()
    passive_mode_event.set()
    load_event: SyncEvent = Event()

    # Queues for GUI messages
    load_path_queue: "Queue[str]" = Queue(1)
    active_mode_queue: "Queue[str]" = Queue(1)
    error_queue: "Queue[BaseException]" = Queue(5)
