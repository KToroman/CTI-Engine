from multiprocessing import Event, Queue
from multiprocessing import Event
from typing import Protocol

from PyQt5.QtCore import pyqtSignal

from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.StatusSettings import StatusSettings


class UIInterface(Protocol):
    """provides an Interface for Implemetations of a User Interface. All contained Methods must be implemented by subclasses."""

    model_queue: Queue
    status_queue: Queue
    error_queue: Queue
    visualize_signal: pyqtSignal
    status_signal: pyqtSignal
    error_signal: pyqtSignal
    """App can insert model-objects for visualization"""

    def deploy_error(self, error: BaseException):
        """receives an Exception, displays information regarding that exception to the user."""
        raise NotImplementedError
    
    def update_statusbar(self, status: StatusSettings):
        """receives a status string, changes the ui's status string accordingly."""
        raise NotImplementedError
    
    def execute(self):
        raise NotImplementedError
