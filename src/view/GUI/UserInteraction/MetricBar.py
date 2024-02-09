from PyQt5.QtWidgets import QPushButton


class MetricBar:
    def __init__(self, metric_frame_layout):
        self.cpu_button = QPushButton("CPU")
        self.cpu_button.setStyleSheet("background-color: #4095a1;")
        self.ram_button = QPushButton("RAM")
        self.ram_button.setStyleSheet("background-color: #4095a1;")
        self.runtime_button = QPushButton("Runtime")
        self.runtime_button.setStyleSheet("background-color: #4095a1;")
        metric_frame_layout.addWidget(self.ram_button)
        metric_frame_layout.addWidget(self.cpu_button)
        metric_frame_layout.addWidget(self.runtime_button)
