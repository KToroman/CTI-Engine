class Plot:

    name: str
    color: str
    x_value: float
    y_value: float
    visibility: bool
    visibility = False

    def __init__(self, name, color, x_value, y_value):
        self.name = name
        self.color = color
        self.x_value = x_value
        self.y_value = y_value