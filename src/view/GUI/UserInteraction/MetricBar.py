from PyQt5.QtWidgets import QCheckBox


class MetricBar:
    def __init__(self, metric_frame_layout, stacked_widget):
        self.cpu_checkbox = QCheckBox("CPU")
        self.ram_checkbox = QCheckBox("RAM")
        self.time_checkbox = QCheckBox("Time")
        metric_frame_layout.addWidget(self.ram_checkbox)
        metric_frame_layout.addWidget(self.cpu_checkbox)
        metric_frame_layout.addWidget(self.time_checkbox)