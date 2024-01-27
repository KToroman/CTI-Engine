from typing import Protocol

class FetcherInterface(Protocol):
    """Interface for fetchers, instances that can make changes to the current project of a model"""

    def update_project(self) -> bool:
        """Changes the current_project of a model instance passed at creation in some way, depending on implementing class """
        raise NotImplementedError