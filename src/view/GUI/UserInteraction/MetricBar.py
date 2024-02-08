from PyQt5.QtWidgets import QPushButton


class MetricBar:
    def __init__(self, metric_frame_layout):
        self.cpu_button = QPushButton("CPU")
        self.ram_button = QPushButton("RAM")
        self.runtime_button = QPushButton("Runtime")
        metric_frame_layout.addWidget(self.ram_button)
        metric_frame_layout.addWidget(self.cpu_button)
        metric_frame_layout.addWidget(self.runtime_button)
