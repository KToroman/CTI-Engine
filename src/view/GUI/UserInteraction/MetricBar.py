from PyQt5.QtWidgets import QPushButton


class MetricBar:
    def __init__(self) -> None:
        self.cpu_button: QPushButton = QPushButton("CPU")
        self.ram_button: QPushButton = QPushButton("RAM")
        self.runtime_button: QPushButton = QPushButton("Runtime")
