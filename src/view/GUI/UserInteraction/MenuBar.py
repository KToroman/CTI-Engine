from PyQt5.QtWidgets import QPushButton, QInputDialog

from src.view.AppRequestsInterface import AppRequestsInterface


class MenuBar:
    def __init__(self, menu_bar_layout, app: AppRequestsInterface):
        self.app = app
        self.load_file_button: QPushButton = QPushButton("Load file")
        self.load_file_button.setStyleSheet("background-color: #61b3bf;")
        self.load_file_button.clicked.connect(lambda: self.show_input_dialog())

        self.pause_resume_button: QPushButton = QPushButton("Restart")
        self.pause_resume_button.clicked.connect(lambda: self.app.restart_measurement())
        self.pause_resume_button.setStyleSheet("background-color: #61b3bf;")

        self.cancel_button: QPushButton = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("background-color: #61b3bf;")
        self.cancel_button.clicked.connect(lambda: self.app.quit_measurement())

        menu_bar_layout.addWidget(self.load_file_button)
        menu_bar_layout.addWidget(self.pause_resume_button)
        menu_bar_layout.addWidget(self.cancel_button)

    def show_input_dialog(self):
        text, ok = QInputDialog.getText(None, "File input", 'Enter file name:')
        if ok:
            self.app.load_path_queue.put(text)
            self.app.load_event.set()
