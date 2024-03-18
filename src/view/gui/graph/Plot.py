from typing import List


class Plot:

    def __init__(self, name, color, x_values, y_values):
        self.name: str = name
        self.color: str = color
        self.x_values: List[float] = x_values
        self.y_values: List[float] = y_values
        self.visibility: bool = False
