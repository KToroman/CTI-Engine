from typing import List


class Plot:

    def __init__(self, name: str, color: str, x_values: List[float], y_values: List[float]):
        self.name: str = name
        self.color: str = color
        self.x_values: List[float] = list()
        self.y_values: List[float] = list()
        self.x_values = x_values
        self.y_values = y_values
