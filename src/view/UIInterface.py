from multiprocessing import Queue
from typing import Protocol

from PyQt5.QtCore import pyqtSignal
from src.model.core.StatusSettings import StatusSettings


class UIInterface(Protocol):
    """provides an Interface for Implementations of a User Interface. All contained Methods must be implemented by
    subclasses."""

    project_queue: "Queue[str]"
    status_queue: "Queue[StatusSettings]"
    error_queue: "Queue[BaseException]"
    visualize_signal: pyqtSignal
    status_signal: pyqtSignal
    error_signal: pyqtSignal
    """App can insert model-objects for visualization"""

    def deploy_error(self) -> None:
        """receives an Exception, displays information regarding that exception to the user."""
        raise NotImplementedError
    
    def update_statusbar(self) -> None:
        """receives a status string, changes the ui's status string accordingly."""
        raise NotImplementedError
    
    def execute(self) -> None:
        raise NotImplementedError
