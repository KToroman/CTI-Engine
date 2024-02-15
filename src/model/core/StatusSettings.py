from enum import Enum


class StatusSettings(Enum):
    """StatusSettings is used to set the status the program is currently in."""
    WAITING = "waiting", "#FFFFFF"  # White
    MEASURING = "measuring", "#FFA500"  # Orange
    LOADING = "loading", "#FFA500"  # Orange
    CANCELLED = "cancelled", "#6d6d6d"  # Grey
    SEARCHING = "searching", "#4095a1"  # Blue
    FINISHED = "finished", "#4CAF50"  # Green
    FAILED = "build failed", "#FF0000"  # Red
    LOADING = "loading your file", "#FFA500"  # Orange
