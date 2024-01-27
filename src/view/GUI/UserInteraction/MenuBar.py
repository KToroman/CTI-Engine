from PyQt5.QtWidgets import QPushButton, QInputDialog


class MenuBar:
    def __init__(self, menu_bar_layout, main_window):
        self.load_file_button : QPushButton = QPushButton("Load file")
        self.load_file_button.clicked.connect(lambda: self.show_input_dialog(main_window))

        self.pause_resume_button : QPushButton = QPushButton("Pause")
        self.pause_resume_button.clicked.connect(lambda: ...)

        self.cancel_button : QPushButton = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: ...)

        menu_bar_layout.addWidget(self.load_file_button)
        menu_bar_layout.addWidget(self.pause_resume_button)
        menu_bar_layout.addWidget(self.cancel_button)

    def show_input_dialog(self, main_window):
        text, ok = QInputDialog.getText(main_window, "File input", 'Enter file name:')
        if ok:
            ... # Rufe Methode aus AppViewInterface auf