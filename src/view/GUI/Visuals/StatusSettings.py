from enum import Enum


class StatusSettings(Enum):
    """StatusSettings is used to set the status the program is currently in."""
    WAITING = "waiting", "#FFFFFF"  # White
    MEASURING = "measuring", "#FFA500"  # Orange
    FINISHED = "finished", "#00FF00"  # Green
    FAILED = "build failed", "#FF0000"  # Red
