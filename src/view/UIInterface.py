from abc import ABC, abstractmethod
from model.ModelReadViewInterface import ModelReadViewInterface

class UIInterface(ABC):
    """provides an Interface for Implemetations of a User Interface. All contained Methods must be implemented by subclasses."""

    @abstractmethod
    def visualize(self, model: ModelReadViewInterface):
        """receives a Model, displays the data contained in that Model to the user."""
        raise NotImplementedError

    @abstractmethod
    def deploy_error(self, error: BaseException):
        """receives an Exception, displays information regarding that exception to the user."""
        raise NotImplementedError
    
    @abstractmethod
    def update_statusbar(self, status: str):
        """receives a status string, changes the ui's status string accordingly."""
        raise NotImplementedError
    
    @abstractmethod
    def run_commands(self):
        """call for the UI to execute all queued commands."""
        raise NotImplementedError
