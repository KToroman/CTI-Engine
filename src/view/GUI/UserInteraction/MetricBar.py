from PyQt5.QtWidgets import QPushButton


class MetricBar:
    def __init__(self):
        self.cpu_button = QPushButton("CPU")
        self.ram_button = QPushButton("RAM")
        self.runtime_button = QPushButton("Runtime")
