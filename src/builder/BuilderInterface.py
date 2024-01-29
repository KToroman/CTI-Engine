from typing import Protocol


class BuilderInterface(Protocol):
    """Interface for builders"""

    def build(self) -> bool:
        """Starts compilation processes for an included header of a given source file.
        Returns true if the processes for all headers of this source file have been completed"""
        raise NotImplementedError
