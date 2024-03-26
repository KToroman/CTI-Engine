from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox

class ErrorWindow(QMessageBox):

    WINDOW_TITLE: str = "Error"

    def __init__(self, exception: BaseException) -> None:
        super().__init__()
        # Setup ErrorWindow
        self.setText(exception.__str__())
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.addButton(QMessageBox.Ok)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(30000)

        # Show immediately
        self.exec_()
