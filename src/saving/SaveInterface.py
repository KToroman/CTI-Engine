from typing import List, Protocol
from src.model.DataBaseEntry import DataBaseEntry

from src.model.core.Project import Project


class SaveInterface(Protocol):
    """SaveInterface is used to save projects."""
    def save_project(self, project: Project, delta: List[DataBaseEntry]):
        """Saves the given project into a file."""
