from PyQt5.QtWidgets import QCheckBox


class MetricBar:
    def __init__(self, metric_frame_layout, stacked_widget):
        self.cpu_checkbox = QCheckBox("CPU")
        self.cpu_checkbox.stateChanged.connect(lambda: ...)
        self.ram_checkbox = QCheckBox("RAM")
        self.ram_checkbox.stateChanged.connect(lambda: ...)
        self.time_checkbox = QCheckBox("Time")
        self.time_checkbox.stateChanged.connect(lambda: stacked_widget.setCurrentIndex(
            1))  # Nur als Beispiel, hier kommt nachher die switch ressources Methode rein
        metric_frame_layout.addWidget(self.ram_checkbox)
        metric_frame_layout.addWidget(self.cpu_checkbox)
        metric_frame_layout.addWidget(self.time_checkbox)