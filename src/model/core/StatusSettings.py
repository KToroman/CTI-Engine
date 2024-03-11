from enum import Enum


class StatusSettings(Enum):
    """StatusSettings is used to set the status the program is currently in."""
    WAITING = "waiting", "#FFFFFF"  # White
    MEASURING = "measuring", "#FFA500"  # Orange
    CANCELLED = "cancelled", "#6d6d6d"  # Grey
    SEARCHING = "searching", "#4095a1"  # Blue
    FINISHED = "finished", "#4CAF50"  # Green
    LOADING = "loading file", "	#add8e6"  # Orange
