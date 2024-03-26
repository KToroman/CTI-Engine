from typing import List, Protocol

from src.model.core.Project import Project


class ModelReadViewInterface(Protocol):
    def get_project_by_name(self, name: str) -> Project:
        """getter for project's name"""
        raise NotImplementedError

    def get_all_project_names(self) -> List[str]:
        raise NotImplementedError

    def get_current_project_name(self) -> str:
        raise NotImplementedError

    def set_visible_project(self, name: str):
        raise NotImplementedError
