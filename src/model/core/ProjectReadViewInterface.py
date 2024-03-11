from typing import Protocol, List

from src.model.core.CFileReadViewInterface import CFileReadViewInterface


class ProjectReadViewInterface(Protocol):

    def get_project_name(self) -> str:
        """getter for project's name"""
        raise NotImplementedError

    def get_cfiles(self) -> List[CFileReadViewInterface]:
        """getter for a view on all cFiles contained in the current project"""
        raise NotImplementedError

    def get_project_time(self) -> float:
        raise NotImplementedError
