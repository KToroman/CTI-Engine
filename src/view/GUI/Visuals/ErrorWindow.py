from PyQt5.QtWidgets import QMessageBox

class ErrorWindow(QMessageBox):

    WINDOW_TITLE: str = "Error"

    def __init__(self, exception: BaseException):
        super().__init__()
        # Setup ErrorWindow
        exception_type = type(exception).__name__
        exception_message = str(exception)

        self.setText(f"Ein Fehler ist aufgetreten:\n{exception_type}")
        self.setInformativeText(f"Weitere Details:\n{exception_message}")
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.addButton(QMessageBox.Ok)
        # Show immediately
        self.exec_()
