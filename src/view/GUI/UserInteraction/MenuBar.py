from typing import List

from PyQt5.QtCore import Qt
from multiprocessing import Queue
from multiprocessing.synchronize import Event as SyncEvent
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QInputDialog, QTextEdit, QScrollArea, QWidget, QVBoxLayout
import qtawesome as qta

from src.view.AppRequestsInterface import AppRequestsInterface


class MenuBar:
    def __init__(self, load_path_queue: Queue, cancel_event: SyncEvent, restart_event: SyncEvent, project_queue: Queue, visualize_event: pyqtSignal):

        self.__project_queue = project_queue
        self.__visualize_event = visualize_event

        self.load_path_queue = load_path_queue
        self.cancel_event = cancel_event
        self.restart_event = restart_event

        self.cancel_icon = qta.icon("ei.ban-circle")

        self.load_file_button: QPushButton = QPushButton("Load file")
        self.load_file_button.setStyleSheet("background-color: #61b3bf;")
        self.load_file_button.clicked.connect(lambda: self.show_input_dialog())

        self.small_load_file_button: QPushButton = QPushButton()
        self.small_load_file_button.setStyleSheet("background-color: #61b3bf;")
        self.small_load_file_button.clicked.connect(lambda: self.show_input_dialog())

        self.pause_resume_button: QPushButton = QPushButton("Restart")
        self.pause_resume_button.clicked.connect(lambda: self.restart_event.set())
        self.pause_resume_button.setStyleSheet("background-color: #61b3bf;")

        self.small_pause_resume_button: QPushButton = QPushButton("icon")
        self.small_pause_resume_button.clicked.connect(lambda: self.restart_event.set())
        self.small_pause_resume_button.setStyleSheet("background-color: #61b3bf;")

        self.cancel_button: QPushButton = QPushButton("Cancel")
        self.cancel_button.setIcon(self.cancel_icon)
        self.cancel_button.setStyleSheet("background-color: #61b3bf;")
        self.cancel_button.clicked.connect(lambda: self.cancel_event.set())

        self.small_cancel_button: QPushButton = QPushButton()
        self.small_cancel_button.setIcon(self.cancel_icon)
        self.small_cancel_button.setStyleSheet("background-color: #61b3bf;")
        self.small_cancel_button.clicked.connect(lambda: self.cancel_event.set())

        self.scroll_bar = QScrollArea()
        self.scroll_bar.setWidgetResizable(True)
        self.scroll_bar.setHidden(True)
        self.scroll_bar.setMaximumSize(135, 500)
        self.scroll_bar.setMinimumHeight(200)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_bar.setWidget(self.scroll_widget)

        self.icon = qta.icon("ei.align-justify")
        self.scroll_button = QPushButton("All Projects")
        self.scroll_button.setIcon(self.icon)
        self.scroll_button.setStyleSheet("background-color: #61b3bf;")
        self.scroll_button.setCheckable(True)
        self.scroll_button.toggled.connect(lambda: self.toggle_scrollbar())



    def show_input_dialog(self):
        text, ok = QInputDialog.getText(None, "File input", 'Enter file name:')
        if ok:
            self.load_path_queue.put(text)



    def show_project_name_input(self, name: str):
        text, ok = QInputDialog.getText(None, "Load Project", "Load the following project?", text= name)
        if ok:
            self.__project_queue.put(name)
            self.__visualize_event.emit()
    def toggle_scrollbar(self):
        # Überprüfen, ob die Scrollbar angezeigt wird oder nicht, und umschalten
        if self.scroll_bar.isHidden():
            self.scroll_bar.setHidden(False)
        else:
            self.scroll_bar.setHidden(True)

        # Das Widget neu zeichnen, um die Änderungen anzuzeigen
        self.scroll_bar.update()

    def update_scrollbar(self, project_names: List[str]):
        if self.scroll_layout.count() > 0:
            for i in range(self.scroll_layout.count()):
                self.scroll_layout.itemAt(i).widget().disconnect()
            while self.scroll_layout.count() > 0:
                item = self.scroll_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        for name in project_names:

            if name.split(" ").__len__() > 2:
                show_name = name.split(" ")[0] + " " + name.split(" ")[-1]
            else:
                show_name = name.split(" ")[0]
            new_button: QPushButton = QPushButton(show_name)
            self.scroll_layout.addWidget(new_button)
            new_button.clicked.connect(lambda: self.show_project_name_input(name))
