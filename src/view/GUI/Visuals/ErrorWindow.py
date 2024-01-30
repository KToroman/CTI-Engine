from PyQt5.QtWidgets import QMessageBox

class ErrorWindow(QMessageBox):

    WINDOW_TITLE: str = "Error"

    def __init__(self, error_message):
        super().__init__()
        # Setup ErrorWindow
        self.setText(error_message)
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.addButton(QMessageBox.Ok)
        # Show immediately
        self.exec_()