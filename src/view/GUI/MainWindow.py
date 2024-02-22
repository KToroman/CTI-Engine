import colorsys
from time import sleep
from src.fetcher.file_fetcher.FileLoader import FileLoader
import os
import sys

import random
from threading import Thread, Lock
from PyQt5.QtCore import QThread
from typing import List
from multiprocessing import Queue, Event
from multiprocessing import Manager

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QApplication, QHBoxLayout, QSplitter, QCheckBox)
from src.model.Model import Model
from src.view.GUI.AppUpdatesThread import AppUpdatesThread
from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.MainWindowMeta import MainWindowMeta
from src.view.GUI.UserInteraction.MenuBar import MenuBar
from src.view.GUI.UserInteraction.TableWidget import TableWidget
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



class MainWindow(QMainWindow, UIInterface, metaclass=MainWindowMeta):
    WINDOWSIZE1: int = 800
    WINDOWSIZE2: int = 600
    WINDOWTITLE: str = "CTI Engine"
    SELECT_ALL: str = "Select all"
    RAM_Y_AXIS: str = "RAM (in mb)"
    CPU_Y_AXIS: str = "CPU (in %)"

    def __init__(self, q_application: QApplication, app: AppRequestsInterface):
        super(MainWindow, self).__init__()
        

        self.__q_application: QApplication = q_application
        self.__app = app

        self.__visible_plots: List[Displayable] = []
        self.project_time: float = 0

        self.setWindowTitle(self.WINDOWTITLE)
        self.resize(self.WINDOWSIZE1, self.WINDOWSIZE2)

        # Setting up the Layout
        self.central_widget: QWidget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        self.top_frame_layout: QHBoxLayout = QHBoxLayout()
        self.main_layout.addLayout(self.top_frame_layout)

        self.user_interaction_frame_layout: QVBoxLayout = QVBoxLayout()
        self.top_frame_layout.addLayout(self.user_interaction_frame_layout)

        self.status_bar_frame_layout: QVBoxLayout = QVBoxLayout()
        self.status_bar: StatusBar = StatusBar()
        self.status_bar.setMaximumHeight(100)
        self.status_bar_frame_layout.addWidget(self.status_bar)
        self.top_frame_layout.addLayout(self.status_bar_frame_layout)
        self.all: QCheckBox = QCheckBox(self.SELECT_ALL)
        self.all.stateChanged.connect(lambda: self.table_widget.toggle_all_rows())
        self.top_frame_layout.addWidget(self.all)

        self.widget_frame_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.addLayout(self.widget_frame_layout)

        self.splitter1: QSplitter = QSplitter(Qt.Horizontal)
        self.widget_frame_layout.addWidget(self.splitter1)

        self.metric_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.menu_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.user_interaction_frame_layout.addLayout(
            self.menu_bar_frame_layout)
        self.user_interaction_frame_layout.addLayout(
            self.metric_bar_frame_layout)

        # Initialize the components
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.ram_graph_widget: GraphWidget = GraphWidget(self.RAM_Y_AXIS)
        self.cpu_graph_widget: GraphWidget = GraphWidget(self.CPU_Y_AXIS)
        self.bar_chart_widget: BarWidget = BarWidget()
        self.stacked_widget.addWidget(self.ram_graph_widget)
        self.stacked_widget.addWidget(self.cpu_graph_widget)
        self.stacked_widget.addWidget(self.bar_chart_widget)
        self.splitter1.addWidget(self.stacked_widget)

        self.table_widget: TableWidget = TableWidget(app)
        self.splitter1.addWidget(self.table_widget)

        self.menu_bar: MenuBar = MenuBar(self.menu_bar_frame_layout, app)
        self.metric_bar: MetricBar = MetricBar(self.metric_bar_frame_layout)

        self.setup_resource_connections()

        images_folder = os.path.join(os.path.dirname(__file__), "Images")
        logo_path = os.path.join(images_folder, "CTIEngineLogo.png")
        icon: QIcon = QIcon(logo_path)
        self.setWindowIcon(icon)
        self.setStyleSheet("background-color: #ECEFF1;")
        """
        colors from cti engine logo:
        #237277
        #4095a1
        #61b3bf
        chatgpt: #ECEFF1
        himmelgrau: #CFD8DC
        caspars farbe: #444447
        """


        

    def __set_up_app_worker(self):
        self.__app_updates_thread: AppUpdatesThread = AppUpdatesThread(self)
        self.__app_updates_thread.start()
        self.__app_updates_thread.run()

    def execute(self, visualize_event, status_queue, model_queue, error_queue):
        # message-queues and events:
        self.error_queue = error_queue

        # queue and event for visualize and status
        self.model_queue = model_queue
        self.status_queue = status_queue
        self.error_queue = error_queue
        self.visualize_event = visualize_event

        model = Model()
        loader = FileLoader("/common/homes/students/upufw_toroman/PSE/simox 2024-02-09", model, Lock())
        loader.update_project()
        self.model_queue.put([model])
        print(self.model_queue.empty())
        self.show()
        self.visualize_event.set()
        self.__set_up_app_worker()

        # TODO set up appupdates worker on a new Thread 
        sys.exit(self.__q_application.exec())
        
    
    def visualize(self, model: ModelReadViewInterface):
        """receives a Model, displays the data contained in that Model to the user."""
        self.project_time = model.get_project_time()
        if self.table_widget.active_started:
            self.__visualize_active(model)
        else:
            self.__visualize_passive(model)

    def __visualize_passive(self, model: ModelReadViewInterface):
        """visualizes data from passive mode."""
        self.table_widget.clear_table()

        # Select spot for Displayables to be inserted into
        self.table_widget.insertion_point = model.get_project_name()

        # Update TableWidget for each cfile
        cfile_list: List[CFileReadViewInterface] = model.get_cfiles()
        for cfile in cfile_list:
            self.table_widget.insert_values(self.__create_displayable(cfile))

        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED)
        self.table_widget.rebuild_table(self.table_widget.rows)

    def __visualize_active(self, model: ModelReadViewInterface):
        """visualizes data from active mode"""

        # Find file used for active build
        active_row: str = self.table_widget.insertion_point
        active_file: CFileReadViewInterface
        for cfile in model.get_cfiles():
            active_file = self.__get_hierarchy(cfile, active_row)
            if active_file.get_name() == active_row:
                break

        # Update TableWidget for header list for said file
        cfile_list: List[CFileReadViewInterface] = active_file.get_headers()
        for cfile in cfile_list:
            # self.table_widget.add_subrow(self.__create_displayable(cfile))
            self.table_widget.fill_subrows(self.__create_displayable(cfile))

        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED)

    def deploy_error(self, error: BaseException):
        """receives an Exception, displays information regarding that exception to the user."""
        error_window = ErrorWindow(error)
        error_window.show()

    def update_statusbar(self, status: StatusSettings):
        """receives a status string, changes the ui's status string accordingly."""
        self.status_bar.update_status(status)

    def __get_hierarchy(self, cfile: CFileReadViewInterface, active_row: str) -> CFileReadViewInterface:
        """finds cfile which started active mode"""
        if cfile.get_name() == active_row:
            return cfile
        elif not cfile.get_headers():
            return None
        for header in cfile.get_headers():
            self.__get_hierarchy(header, active_row)

    def __create_displayable(self, cfile: CFileReadViewInterface) -> Displayable:
        """turns given cfile into displayable"""

        # Collect data for Displayable
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

        # Create header and secondary header list for current Displayable
        headers: List[str] = list()
        secondary_headers: List[List[str]] = list()
        for header in cfile.get_headers():
            headers.append(header.get_name())
            subheaders: List[str] = []
            for secondary_header in header.get_headers():
                subheaders.append(secondary_header.get_name())
            secondary_headers.append(subheaders)
        return Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, headers, secondary_headers)

    def __generate_random_color(self):
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
        """sets up connections between table and graph widgets"""
        for row in self.table_widget.rows:
            if not row.connected:
                row.checkbox.stateChanged.connect(
                    lambda state, current_row=row: self.update_visibility(current_row.displayable))
                row.connected = True

        self.setup_click_connections()

    def setup_resource_connections(self):
        """sets up connections between metric bar and graph/bar chart widgets"""
        self.metric_bar.cpu_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.metric_bar.ram_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.metric_bar.runtime_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(2))

    def update_visibility(self, displayable: Displayable):
        """shows or hides plots of given displayable"""
        visibility: bool = False
        for visible_displayable in self.__visible_plots:
            if visible_displayable.name == displayable.name:
                visibility = True
                self.__visible_plots.remove(visible_displayable)
                self.__remove_from_graph(displayable)
        if not visibility:
            self.__visible_plots.append(displayable)
            self.__add_to_graph(displayable)

    def __add_to_graph(self, displayable: Displayable):
        """adds plots of given displayable to graph and bar chart widgets"""
        Thread(target=self.ram_graph_widget.add_plot, args=[displayable.ram_plot]).start()
        Thread(target=self.cpu_graph_widget.add_plot, args=[displayable.cpu_plot]).start()
        self.bar_chart_widget.add_bar(displayable.runtime_plot)

    def __remove_from_graph(self, displayable: Displayable):
        """removes plots of given displayable from graph and bar chart widgets"""
        Thread(target=self.ram_graph_widget.remove_plot, args=[displayable.ram_plot]).start()
        Thread(target=self.cpu_graph_widget.remove_plot, args=[displayable.cpu_plot]).start()
        self.bar_chart_widget.remove_bar(displayable.runtime_plot)

    def setup_click_connections(self):
        self.bar_chart_widget.click_signal.connect(
            lambda: self.table_widget.highlight_row(self.bar_chart_widget.bar_clicked))
        self.cpu_graph_widget.click_signal.connect(
            lambda: self.table_widget.highlight_row(self.cpu_graph_widget.plot_clicked))
        self.ram_graph_widget.click_signal.connect(
            lambda: self.table_widget.highlight_row(self.ram_graph_widget.plot_clicked))

    def closeEvent(self, a0: QCloseEvent):
        self.__app_updates_thread.shutdown_event.set()
        self.__app.shutdown_event.set()
