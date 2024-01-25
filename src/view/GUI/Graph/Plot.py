class Plot:

    name: str
    color: str
    x_values: list[:float]
    y_values: list[:float]
    visibility: bool
    visibility = False

    def __init__(self, name, color, x_values, y_values):
        self.name = name
        self.color = color
        self.x_values = x_values
        self.y_values = y_values