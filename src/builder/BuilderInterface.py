from typing import Protocol
from src.model.core.Header import Header


class BuilderInterface(Protocol):
    """Interface for builders"""

    def build(self) -> bool:
        """Starts compilation processes for the next included header of a given source file.
        Returns false if the processes for all headers of this source file have been completed, otherwise true"""
        raise NotImplementedError
    
    def get_next_header(self) -> Header:
        """fetches the next header waiting to be built."""
        raise NotImplementedError

    def clear_directory(self) -> None:
        """Clears the build directory"""
        raise NotImplementedError
