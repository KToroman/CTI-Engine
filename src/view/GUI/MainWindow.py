import colorsys

import os

import random
import time

from PyQt5.QtCore import pyqtSignal, QThread
from threading import Thread, Lock
from PyQt5.QtCore import pyqtSignal, QThreadPool
from typing import List
from multiprocessing import Queue, Event

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QApplication, QHBoxLayout, QSplitter, QCheckBox, QSpinBox, QLineEdit,
                             QPushButton)
from src.model.Model import Model
from src.model.core.ProjectReadViewInterface import ProjectReadViewInterface
from src.view.GUI.PlotRunnable import PlotRunnable
from src.view.GUI.AddRunnable import AddRunnable
from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.MainWindowMeta import MainWindowMeta
from src.view.GUI.RemoveRunnable import RemoveRunnable
from src.view.GUI.UserInteraction.DisplayableHolder import DisplayableHolder
from src.view.GUI.UserInteraction.MenuBar import MenuBar
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.MetricBar import MetricBar
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.view.GUI.Graph.Plot import Plot
from src.model.core.MetricName import MetricName
from src.view.GUI.Visuals.StatusBar import StatusBar
from src.model.core.StatusSettings import StatusSettings
from src.view.UIInterface import UIInterface
from src.view.GUI.Visuals.ErrorWindow import ErrorWindow
from src.view.AppRequestsInterface import AppRequestsInterface
import src.view.GUI.Visuals.GuiDesign as gd
from src.view.GUI.UserInteraction.TreeWidget import TreeWidget, get_new_Treewidget


class MainWindow(QMainWindow, UIInterface, metaclass=MainWindowMeta):
    WINDOWSIZE1: int = 800
    WINDOWSIZE2: int = 600
    WINDOWTITLE: str = "CTI Engine"
    SELECT_ALL: str = "Select all"
    RAM_Y_AXIS: str = "RAM (in mb)"
    CPU_Y_AXIS: str = "CPU (in %)"

    error_signal: pyqtSignal = pyqtSignal()
    visualize_signal: pyqtSignal = pyqtSignal()
    status_signal: pyqtSignal = pyqtSignal()
    change_table_signal: pyqtSignal = pyqtSignal()
    index_queue: Queue = Queue()

    def __init__(self, shutdown_event: Event, q_application: QApplication, status_queue: Queue, project_queue: Queue,
                 error_queue: Queue, load_path_queue: Queue, active_mode_queue: Queue, cancel_event: Event,
                 restart_event: Event, model: ModelReadViewInterface):
        super(MainWindow, self).__init__()

        # Queues and events for communication between app and gui
        self.project_queue: Queue = project_queue
        self.visualize_signal.connect(lambda: self.visualize())

        self.change_table_signal.connect(lambda: self.toggle_table_vis(self.index_queue.get()))

        self.__model = model
        self.active_mode_queue = active_mode_queue
        self.table_widget: TreeWidget = TreeWidget(active_mode_queue)
        self.status_queue: Queue = status_queue
        self.status_signal.connect(lambda: self.update_statusbar())

        self.error_queue: Queue = error_queue
        self.error_signal.connect(lambda: self.deploy_error())
        self.shutdown_event: Event = shutdown_event

        self.__q_application: QApplication = q_application
        self.__visible_plots: List[Displayable] = []
        self.project_time: float = 0
        self.HIERARCHY_DEPTH: int = 3
        self.thread_pool: QThreadPool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(10)

        self.setWindowTitle(self.WINDOWTITLE)
        self.resize(self.WINDOWSIZE1, self.WINDOWSIZE2)

        self.select_all_checkbox = QCheckBox("select all")
        self.upper_limit = QSpinBox()
        self.lower_limit = QSpinBox()

        self.menu_bar: MenuBar = MenuBar(load_path_queue, cancel_event, restart_event, self.project_queue,
                                         self.visualize_signal, self.index_queue, self.change_table_signal)
        self.metric_bar: MetricBar = MetricBar()

        self.setup_resource_connections()

        images_folder = os.path.join(os.path.dirname(__file__), "Images")
        logo_path = os.path.join(images_folder, "CTIEngineLogo.png")
        icon: QIcon = QIcon(logo_path)
        self.setWindowIcon(icon)
        self.setStyleSheet("background-color: #ECEFF1;")

        """colors from cti engine logo:
        #237277
        #4095a1
        #61b3bf
        chatgpt: #ECEFF1
        himmelgrau: #CFD8DC
        caspars farbe: #444447"""

        self.ram_graph_widget: GraphWidget = GraphWidget(self.RAM_Y_AXIS)
        self.cpu_graph_widget: GraphWidget = GraphWidget(self.CPU_Y_AXIS)
        self.bar_chart_widget: BarWidget = BarWidget()

        self.stacked_widget = QStackedWidget()

        self.status_bar: StatusBar = StatusBar()
        self.setup_resource_connections()

        self.displayed_project: str = ""

        self.line_edit = QLineEdit()
        self.search_button = QPushButton()

        self.current_table: TreeWidget = self.table_widget
        self.all_tables: List[TreeWidget] = []
        self.stacked_table_widget: QStackedWidget = QStackedWidget()
        self.__connect_new_table()
        gd.setupUI(self)

    def execute(self):
        self.show()
        self.__q_application.exec()

    def visualize(self):
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.setChecked(False)
        """displays the data contained in that Model to the user."""
        project_name: str = self.project_queue.get()
        project = self.__model.get_project_by_name(project_name)
        self.project_time = project.get_project_time()
        self.displayed_project = project_name
        self.__update_project_list(self.displayed_project)
        if self.current_table.active_started:
            self.__visualize_active(project)
            self.current_table.active_started = False
        else:
            self.__visualize_passive(project)

    def __visualize_passive(self, project: ProjectReadViewInterface):
        print("[MW]    in visualize passive")
        tima = time.time()
        #self.__connect_new_table()
        """Visualizes data from passive mode."""
        # Select spot for Displayables to be inserted into
        # self.current_table.clear_tree()
        print("[MW]    now going through cfiles")
        # Update TableWidget for each cfile
        cfile_list: List[CFileReadViewInterface] = project.get_cfiles()
        file_count: int = 1
        displayable_list: List[DisplayableHolder] = []
        for cfile in cfile_list:
            file_count += 1
            displayable_list.append(self.__create_displayable(cfile, 0))
        print("[MW]    all displayables created " + (time.time()-tima).__str__())
        timo = time.time()
        get_new_Treewidget(self, self.active_mode_queue, displayable_list)
        self.current_table.insertion_point = project.get_project_name()
        print("[MW]    insert values finished " + (time.time() - timo).__str__())
        self.lower_limit.setMaximum(file_count)
        self.upper_limit.setMaximum(file_count)
        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED, project.get_project_name())

        self.menu_bar.project_buttons[len(self.menu_bar.project_buttons) - 1].setStyleSheet("background-color: #00FF00")

    def __visualize_active(self, project: ProjectReadViewInterface):
        """Visualizes data from active mode."""
        # Find file used for active build
        active_row: str = self.current_table.insertion_point
        active_file: CFileReadViewInterface
        for cfile in project.get_cfiles():
            if cfile.get_name() == active_row:
                active_file = cfile
                break

        # Update TableWidget for header list for said file
        cfile_list: List[CFileReadViewInterface] = active_file.get_headers()
        time1 = time.time()
        for cfile in cfile_list:
            self.current_table.add_active_data(self.__create_displayable(cfile, 1))
        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED, project.get_project_name())
        print("updated")

    def __connect_new_table(self):
        self.connect_table(TreeWidget(self.active_mode_queue))

    def connect_table(self, table: TreeWidget):
        print("connect")
        self.current_table: TreeWidget = table
        self.stacked_table_widget.addWidget(self.current_table)
        self.all_tables.append(self.current_table)
        self.select_all_checkbox.disconnect()
        self.select_all_checkbox.stateChanged.connect(lambda: self.current_table.toggle_all_rows())
        self.upper_limit.editingFinished.connect(
            lambda: self.current_table.toggle_custom_amount(self.lower_limit.value(), self.upper_limit.value()))
        self.lower_limit.editingFinished.connect(
            lambda: self.current_table.toggle_custom_amount(self.lower_limit.value(), self.upper_limit.value()))
        self.search_button.clicked.connect(lambda: self.current_table.search_item(self))
        self.stacked_table_widget.setCurrentIndex(self.stacked_table_widget.count() - 1)

    def toggle_table_vis(self, index: int):
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.setChecked(False)
        self.stacked_table_widget.setCurrentIndex(index + 1)
        self.current_table = self.all_tables[index + 1]

    def deploy_error(self):
        """Receives an Exception, displays information regarding that exception to the user."""
        if self.error_queue.empty():
            return
        error = self.error_queue.get()
        error_window = ErrorWindow(error)
        error_window.show()

    def update_statusbar(self):
        """Receives a status string, changes the UI's status string accordingly."""
        status = self.status_queue.get()
        if status.value[0] == "measuring":
            self.status_bar.update_status(status, self.__model.get_current_project_name())
        elif status.value[0] == "active measuring":
            self.status_bar.update_status(status, self.current_table.insertion_point.split(".o")[0].split("/")[-1])
        elif status.value[0] == "loading file":
            self.status_bar.update_status(status, self.menu_bar.load_path_name)
        else:
            self.status_bar.update_status(status, "")

    def __get_hierarchy(self, cfile: CFileReadViewInterface, active_row: str) -> CFileReadViewInterface:
        """Finds cfile which started active mode."""
        if cfile.get_name() == active_row:
            return cfile
        elif not cfile.get_headers():
            return None
        for header in cfile.get_headers():
            self.__get_hierarchy(header, active_row)

    def __create_displayable(self, cfile: CFileReadViewInterface, depth_p: int) -> DisplayableHolder:
        """turns given cfile into displayable"""
        depth = depth_p + 1
        if depth >= self.HIERARCHY_DEPTH or not cfile.get_headers():
            return DisplayableHolder(self.__make_disp(cfile), [])
        sub_disp_list: List[DisplayableHolder] = list()
        for h in cfile.get_headers():
            sub_disp_list.append(self.__create_displayable(h, depth))
        return DisplayableHolder(self.__make_disp(cfile), sub_disp_list)

    def __make_disp(self, cfile: CFileReadViewInterface) -> Displayable:
        name: str = cfile.get_name()
        ram_peak: float = cfile.get_max(MetricName.RAM)
        cpu_peak: float = cfile.get_max(MetricName.CPU)
        # Create Graph Plots
        x_values: List[float] = list()
        for c in cfile.get_timestamps():
            x_values.append(c - self.project_time)
        ram_y_values: List[float] = cfile.get_metrics(MetricName.RAM)
        cpu_y_values: List[float] = cfile.get_metrics(MetricName.CPU)
        runtime: List[float] = [cfile.get_total_time()]
        color: str = self.__generate_random_color()
        ram_plot = Plot(name, color, x_values, ram_y_values)
        cpu_plot = Plot(name, color, x_values, cpu_y_values)
        runtime_plot = Plot(name, color, None, runtime)
        return Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, cfile.has_error())

    def __generate_random_color(self) -> str:
        """Generates random saturated color between light blue and pink."""
        light_blue_rgb = (173, 216, 230)  # Light Blue
        pink_rgb = (255, 182, 193)  # Pink
        saturation_factor = 2.1

        # Generate random RGB Values between Light Blue and Pink
        random_color_rgb = [
            random.randint(min(light_blue_rgb[i], pink_rgb[i]), max(light_blue_rgb[i], pink_rgb[i]))
            for i in range(3)
        ]

        hsv = colorsys.rgb_to_hsv(random_color_rgb[0] / 255.0, random_color_rgb[1] / 255.0, random_color_rgb[2] / 255.0)
        hsv = (hsv[0], min(1.0, hsv[1] * saturation_factor), hsv[2])
        random_color_rgb = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(*hsv))
        random_color_hex = "#{:02X}{:02X}{:02X}".format(*random_color_rgb)

        return random_color_hex

    def setup_connections(self):
        """Sets up connections between table and graph widgets."""
        for row in self.current_table.rows:
            if not row.connected:
                row.checkbox.stateChanged.connect(
                    lambda state, current_row=row: self.update_visibility(current_row.displayable))
                row.connected = True

        self.setup_click_connections()

    def setup_resource_connections(self):
        """Sets up connections between metric bar and graph/bar chart widgets."""
        self.metric_bar.cpu_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.metric_bar.ram_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.metric_bar.runtime_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(2))

    def update_visibility(self, displayable: Displayable):
        """Shows or hides plots of given displayable."""
        visibility: bool = False
        for visible_displayable in self.__visible_plots:
            if visible_displayable.name == displayable.name:
                visibility = True
                self.__visible_plots.remove(visible_displayable)
                remove_runnable: RemoveRunnable = RemoveRunnable(ram_graph=self.ram_graph_widget,
                                                                 cpu_graph=self.cpu_graph_widget,
                                                                 runtime_graph=self.bar_chart_widget,
                                                                 displayable=displayable)
                self.thread_pool.start(remove_runnable)
        if not visibility:
            self.__visible_plots.append(displayable)
            add_runnable: AddRunnable = AddRunnable(ram_graph=self.ram_graph_widget,
                                                    cpu_graph=self.cpu_graph_widget,
                                                    runtime_graph=self.bar_chart_widget, displayable=displayable)
            self.thread_pool.start(add_runnable)
        if not self.current_table.in_row_loop:
            plot_runnable: PlotRunnable = PlotRunnable(ram_graph=self.ram_graph_widget, cpu_graph=self.cpu_graph_widget,
                                                       runtime_graph=self.bar_chart_widget)
            self.thread_pool.start(plot_runnable)

    def setup_click_connections(self):
        """Sets up connections between clicking on graph and highlighting according table row."""
        self.bar_chart_widget.click_signal.connect(
            lambda: self.current_table.highlight_row(self.bar_chart_widget.bar_clicked))
        self.cpu_graph_widget.click_signal.connect(
            lambda: self.current_table.highlight_row(self.cpu_graph_widget.plot_clicked))
        self.ram_graph_widget.click_signal.connect(
            lambda: self.current_table.highlight_row(self.ram_graph_widget.plot_clicked))

    def __update_project_list(self, project_name: str):
        self.menu_bar.update_scrollbar(self.__model.get_all_project_names(), project_name)

    def closeEvent(self, event):
        self.shutdown_event.set()
        event.accept()
