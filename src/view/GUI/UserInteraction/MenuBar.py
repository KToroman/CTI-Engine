import typing
from multiprocessing import Queue
from multiprocessing.synchronize import Event as SyncEvent
from typing import List
from PyQt5.QtWidgets import QPushButton, QInputDialog, QTextEdit, QScrollArea, QWidget, QVBoxLayout, QComboBox

from src.model.core.ProjectReadViewInterface import ProjectReadViewInterface
from src.view.AppRequestsInterface import AppRequestsInterface
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QPushButton, QInputDialog, QScrollArea, QWidget, QVBoxLayout
from src.view.GUI.UserInteraction.ProjectNameButtonWrapper import ProjectNameButton


class MenuBar:
    def __init__(self, load_path_queue: "Queue[str]", cancel_event: SyncEvent, restart_event: SyncEvent,
                 project_queue: "Queue[str]", visualize_event: pyqtSignal, index_queue: "Queue[int]",
                 change_table_signal: pyqtSignal) -> None:

        self.__project_queue: "Queue[str]" = project_queue
        self.__visualize_event: pyqtSignal = visualize_event  # type: ignore[call-overload]

        self.index_queue: "Queue[int]" = index_queue
        self.change_table_signal: pyqtSignal = change_table_signal  # type: ignore[call-overload]

        self.load_path_queue: "Queue[str]" = load_path_queue
        self.load_path_name: str = ""
        self.cancel_event: SyncEvent = cancel_event
        self.restart_event: SyncEvent = restart_event

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
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(2)
        self.scroll_bar.setWidget(self.scroll_widget)

        self.scroll_button = QPushButton("All Projects")
        self.scroll_button.setCheckable(True)
        self.scroll_button.toggled.connect(lambda: self.__toggle_scrollbar())

        self.project_buttons: List[QPushButton] = []


    def __show_input_dialog(self) -> None:
        """opens an input dialog to enter a path of a project"""
        text, ok = QInputDialog.getText(self.scroll_widget, "File input", 'Enter file name:')
        if ok:
            self.load_path_queue.put(text)
            self.load_path_name = text.split("/")[-1]

    def __toggle_scrollbar(self) -> None:
        """change the visibility of the scroll area located in the menu bar"""
        if self.scroll_bar.isHidden():
            self.scroll_bar.setHidden(False)
        else:
            self.scroll_bar.setHidden(True)
        self.scroll_bar.update()

    def update_scrollbar(self, project_names: List[str]) -> None:
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
                    self.project_buttons.remove(typing.cast(QPushButton, widget))
                    widget.deleteLater()
                    pass
        # split the displayed name to only the last part
        for name in project_names:
            show_name = name.split("__")[0]
            # put new buttons in
            new_button = ProjectNameButton(self.project_buttons, show_name, name, self.__project_queue,
                                           self.__visualize_event, self.index_queue, self.change_table_signal)
            self.scroll_layout.addWidget(new_button, alignment=Qt.AlignTop)
            self.project_buttons.append(new_button)

    def set_stylesheet(self, style: str) -> None:
        if style == "Dark Mode Purple":
            self.load_file_button.setStyleSheet("background-color: #476eed;")
            self.pause_resume_button.setStyleSheet("background-color: #476eed;")
            self.cancel_button.setStyleSheet("background-color: #476eed;")
            self.scroll_button.setStyleSheet("background-color: #476eed;")
            self.scroll_widget.setStyleSheet("background-color: #252526;")
        if style == "Dark Mode" or style == "Basic":
            self.load_file_button.setStyleSheet("background-color: #23868B;")
            self.pause_resume_button.setStyleSheet("background-color: #23868B;")
            self.cancel_button.setStyleSheet("background-color: #23868B;")
            self.scroll_button.setStyleSheet("background-color: #23868B;")
            self.scroll_widget.setStyleSheet("background-color: #252526;")
        if style == "Light Mode":
            self.load_file_button.setStyleSheet("background-color: #8D9FD0;")
            self.pause_resume_button.setStyleSheet("background-color: #8D9FD0;")
            self.cancel_button.setStyleSheet("background-color: #8D9FD0;")
            self.scroll_button.setStyleSheet("background-color: #8D9FD0;")
            self.scroll_widget.setStyleSheet("background-color: #252526;")
