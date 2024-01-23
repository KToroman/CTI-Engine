from typing_extensions import Protocol

from core.CFileReadViewInterface import CFileReadViewInterface

class ModelReadViewInterface(Protocol):

    '''getter for project's name'''
    def get_project_name() -> str:
        raise NotImplementedError
    
    '''getter for a view on all cFiles contained in the current project'''
    def get_cfiles() -> list[:CFileReadViewInterface]:
        raise NotImplementedError