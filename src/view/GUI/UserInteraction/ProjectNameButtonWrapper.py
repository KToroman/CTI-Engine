from PyQt5.QtWidgets import QPushButton


class ProjectNameButton(QPushButton):
    def __init__(self, project_buttons, show_name, project_name, project_queue, visualize_event, *__args):
        super().__init__(*__args)
        self.show_name = show_name
        self.project_name = project_name
        self.__project_queue = project_queue
        self.__visualize_event = visualize_event
        self.setText(show_name)
        self.clicked.connect(lambda: self.show_project_name_input(project_name))
        self.button_list = project_buttons

    def show_project_name_input(self, name: str):
        sender = self.sender()
        for button in self.button_list:
            if button is sender:
                button.setStyleSheet("background-color: #00FF00")  # Setze Farbe des angeklickten Buttons
            else:
                button.setStyleSheet("")
        text, ok = QInputDialog.getText(None, "Load Project", "Load the following project?", text=name)
        if ok:
            self.__project_queue.put(name)
            self.__visualize_event.emit()
