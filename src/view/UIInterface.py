from multiprocessing import Event, Queue
from multiprocessing import Event
from typing import Protocol
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.StatusSettings import StatusSettings


class UIInterface(Protocol):
    """provides an Interface for Implemetations of a User Interface. All contained Methods must be implemented by subclasses."""

    model_queue: Queue
    visualize = Event()
    status_queue: Queue
    error_queue: Queue
    """App can insert model-objects for visualization"""

    def deploy_error(self, error: BaseException):
        """receives an Exception, displays information regarding that exception to the user."""
        raise NotImplementedError
    
    def update_statusbar(self, status: StatusSettings):
        """receives a status string, changes the ui's status string accordingly."""
        raise NotImplementedError
    
    def execute(self, status_queue, error_queue, model_queue, visualize_event):
        raise NotImplementedError
