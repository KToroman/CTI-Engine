from typing import List


class Plot:

    def __init__(self, name: str, color: str, x_values: list[float], y_values: list[float]) -> None:

        self.name: str = name
        self.color: str = color
        self.x_values: List[float] = x_values
        self.y_values: List[float] = y_values
        self.visibility: bool = False
