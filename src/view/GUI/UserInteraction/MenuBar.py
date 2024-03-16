from multiprocessing import Queue
from multiprocessing.synchronize import Event as SyncEvent
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QInputDialog, QTextEdit, QScrollArea, QWidget, QVBoxLayout, QComboBox
import qtawesome as qta

from src.view.AppRequestsInterface import AppRequestsInterface
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QInputDialog, QScrollArea, QWidget, QVBoxLayout
from src.view.GUI.UserInteraction.ProjectNameButtonWrapper import ProjectNameButton


class MenuBar:
    def __init__(self, load_path_queue: Queue, cancel_event: SyncEvent, restart_event: SyncEvent, project_queue: Queue,
                 visualize_event: pyqtSignal, index_queue: Queue, change_table_signal: pyqtSignal):

        self.__project_queue = project_queue
        self.__visualize_event = visualize_event

        self.index_queue = index_queue
        self.change_table_signal = change_table_signal

        self.load_path_queue = load_path_queue
        self.load_path_name: str = ""
        self.cancel_event = cancel_event
        self.restart_event = restart_event

        self.load_file_button: QPushButton = QPushButton("Load file")
        self.load_file_button.clicked.connect(lambda: self.__show_input_dialog())

        self.pause_resume_button: QPushButton = QPushButton("Restart")
        self.pause_resume_button.clicked.connect(lambda: self.restart_event.set())

        self.cancel_button: QPushButton = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.cancel_event.set())

        self.switch_style_box: QComboBox = QComboBox()

        self.scroll_bar: QScrollArea = QScrollArea()

        self.scroll_widget: QWidget = QWidget()
        self.scroll_layout: QVBoxLayout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(2)
        self.scroll_bar.setWidget(self.scroll_widget)

        self.scroll_button = QPushButton("All Projects")
        self.scroll_button.setCheckable(True)
        self.scroll_button.toggled.connect(lambda: self.__toggle_scrollbar())

        self.project_buttons: List[QPushButton] = []


    def __show_input_dialog(self):
        """opens an input dialog to enter a path of a project"""
        text, ok = QInputDialog.getText(self.scroll_widget, "File input", 'Enter file name:')
        if ok:
            self.load_path_queue.put(text)
            self.load_path_name = text.split("/")[-1]

    def __toggle_scrollbar(self):
        """change the visibility of the scroll area located in the menu bar"""
        if self.scroll_bar.isHidden():
            self.scroll_bar.setHidden(False)
        else:
            self.scroll_bar.setHidden(True)
        self.scroll_bar.update()

    def update_scrollbar(self, project_names: List[str]):
        """updates the scroll area when a new project is about to be visualized so all loaded projects are
            correctly displayed in the scroll area"""
        #delete and disconnect the existing buttons in the scroll area
        if self.scroll_layout.count() > 0:
            for i in range(self.scroll_layout.count()):
                self.scroll_layout.itemAt(i).widget().disconnect()
            while self.scroll_layout.count() > 0:
                item = self.scroll_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    self.project_buttons.remove(widget)
                    widget.deleteLater()
                    pass
        # split the displayed name to only the last part
        for name in project_names:
            if name.split(" ").__len__() > 2:
                show_name = name.split(" ")[0] + " " + name.split(" ")[-1]
            else:
                show_name = name.split(" ")[0]
            # put new buttons in
            new_button = ProjectNameButton(self.project_buttons, show_name, name, self.__project_queue,
                                           self.__visualize_event, self.index_queue, self.change_table_signal)
            self.scroll_layout.addWidget(new_button)
            self.project_buttons.append(new_button)
