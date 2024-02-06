from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from src.view.GUI.Visuals.StatusSettings import StatusSettings


class StatusBar(QWidget):
    """StatusBar is used to display the program's status."""
    WINDOW_SIZE: int = 20
    SPACING: int = 10
    STATUS_TEXT: str = "Status: "

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
        self.update_status(StatusSettings.WAITING)

    def update_status(self, status: StatusSettings):
        """Updates the statusbar according to a given setting."""
        self.status_message.setText(self.STATUS_TEXT + status.value[0])
        self.color_window.setStyleSheet(f"background-color: {status.value[1]}")
        self.update()
