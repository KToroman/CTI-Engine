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
        # Show immediately
        self.exec_()
