from typing_extensions import Protocol
from typing import List

from core.CFileReadViewInterface import CFileReadViewInterface


class ModelReadViewInterface(Protocol):

    def get_project_name() -> str:
        '''getter for project's name'''
        raise NotImplementedError

    def get_cfiles() -> List[CFileReadViewInterface]:
        '''getter for a view on all cFiles contained in the current project'''
        raise NotImplementedError
