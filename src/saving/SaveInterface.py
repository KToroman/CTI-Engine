from typing import List, Protocol
from src.model.DataBaseEntry import DataBaseEntry


class SaveInterface(Protocol):
    """SaveInterface is used to save projects."""
    def save_project(self, project_name: str):
        """Saves the given project into a file."""
