from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout

class StatusBar(QWidget):

    WINDOW_SIZE: int = 20
    SPACING: int = 10
    STATUS_TEXT: str = "Status: "
    # Colors
    WHITE: str = "#FFFFFF"
    ORANGE: str = "#FFA500"
    GREEN: str = "#00FF00"
    RED: str = "#FF0000"
    # Status Settings
    WAITING: str = "waiting"
    MEASURING: str = "measuring"
    FINISHED: str = "finished"
    FAILED: str = "build failed"

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