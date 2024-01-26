from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout

class StatusBar(QWidget):

    WINDOW_SIZE = 20
    SPACING = 10
    STATUS_TEXT = "Status: "
    # Colors
    WHITE = "#FFFFFF"
    ORANGE = "#FFA500"
    GREEN = "#00FF00"
    RED = "#FF0000"
    # Status Settings
    WAITING = "waiting"
    MEASURING = "measuring"
    FINISHED = "finished"
    FAILED = "build failed"

    def __init__(self):
        super().__init__()
        # Create Components of StatusBar
        self.status_message = QLabel(self)
        self.color_window = QLabel(self)
        self.color_window.setFixedSize(self.WINDOW_SIZE, self.WINDOW_SIZE)
        # Setup Layout for StatusBar
        layout = QHBoxLayout(self)
        layout.addWidget(self.color_window)
        layout.addWidget(self.status_message)
        layout.setSpacing(self.SPACING)
        self.setLayout(layout)
        # Initialize StatusBar to WAITING
        self.update_status(self.WAITING)

    def update_status(self, status):
        status_settings = {
            self.WAITING: self.WHITE,
            self.MEASURING: self.ORANGE,
            self.FINISHED: self.GREEN,
            self.FAILED: self.RED
        }
        self.status_message.setText(self.STATUS_TEXT + status)
        self.color_window.setStyleSheet(f"background-color: {status_settings[status]}")
        self.update()