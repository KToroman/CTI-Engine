import sys

import random
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QCheckBox, QApplication, QHBoxLayout, QSplitter)
from Graph.BarWidget import BarWidget
from Graph.GraphWidget import GraphWidget
from UserInteraction.MenuBar import MenuBar
from UserInteraction.TableWidget import TableWidget
from UserInteraction.Displayable import Displayable
from UserInteraction.MetricBar import MetricBar
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.view.GUI.Graph.Plot import Plot
from src.model.core.MetricName import MetricName
from src.view.GUI.Visuals.StatusBar import StatusBar


class MainWindow(QMainWindow):
    WINDOWSIZE1: int = 800
    WINDOWSIZE2: int = 600
    WINDOWTITLE: str = "CTI Engine"

    def __init__(self):
        super().__init__()
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

        self.status_bar_frame_layout: QHBoxLayout = QVBoxLayout()
        self.status_bar: StatusBar = StatusBar()
        self.status_bar.setMaximumHeight(100)
        self.status_bar_frame_layout.addWidget(self.status_bar)
        self.top_frame_layout.addLayout(self.status_bar_frame_layout)

        self.widget_frame_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.addLayout(self.widget_frame_layout)

        self.splitter1: QSplitter = QSplitter(Qt.Horizontal)
        self.widget_frame_layout.addWidget(self.splitter1)

        self.metric_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.menu_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.user_interaction_frame_layout.addLayout(self.menu_bar_frame_layout)
        self.user_interaction_frame_layout.addLayout(self.metric_bar_frame_layout)

        # Initialize the components
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.page_1: GraphWidget = GraphWidget()  # Hier später die implementierte Version von GraphWidget
        self.page_2: BarWidget = BarWidget()  # Hier später die implementierte Version von BarWidget
        self.stacked_widget.addWidget(self.page_1)
        self.stacked_widget.addWidget(self.page_2)
        self.splitter1.addWidget(self.stacked_widget)

        self.table_widget: TableWidget = TableWidget()
        self.splitter1.addWidget(self.table_widget)

        self.menu_bar: MenuBar = MenuBar(self.menu_bar_frame_layout, self)
        self.metric_bar: MetricBar = MetricBar(self.metric_bar_frame_layout, self.stacked_widget)

        # Test nur als Beispiel
        self.dis = Displayable("abc", ..., ..., ..., 39, 123, 123)
        self.dis1 = Displayable("def", ..., ..., ..., 39, 123, 123)
        self.dis2 = Displayable("xyz", ..., ..., ..., 39, 123, 123)

        self.table_widget.insert_values(self.dis)
        self.table_widget.insert_values(self.dis1)
        self.table_widget.insert_values(self.dis2)


    def visualize(self, model):
        # Select spot for Displayables to be inserted into
        self.table_widget.insertion_point = model.get_project_name()

        # Update TableWidget for each cfile
        cfile_list: List[CFileReadViewInterface] = model.get_cfiles()
        for cfile in cfile_list:
            self.table_widget.insert_values(self.__create_displayable(cfile))

        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status("finished")

    # Possibly some mistakes here, needs testing
    def visualize_active(self, model: ModelReadViewInterface):
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
            self.table_widget.add_subrow(self.__create_displayable(cfile))

        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status("finished")

    # Find cfile which started active mode
    def __get_hierarchy(self, cfile: CFileReadViewInterface, active_row: str) -> CFileReadViewInterface:
        if cfile.get_name() == active_row:
            return cfile
        elif not cfile.get_headers():
            return None
        for header in cfile.get_headers():
            self.__get_hierarchy(header, active_row)

    # Create displayable
    def __create_displayable(self, cfile: CFileReadViewInterface) -> Displayable:

        # Collect data for Displayable
        name: str = cfile.get_name()
        ram_peak: float = cfile.get_max(MetricName.RAM)
        cpu_peak: float = cfile.get_max(MetricName.CPU)

        # Create Graph Plots
        x_values: List[float] = cfile.get_timestamp()
        ram_y_values: List[float] = cfile.get_metrics(MetricName.RAM)
        cpu_y_values: List[float] = cfile.get_metrics(MetricName.CPU)
        runtime: List[float] = [cfile.get_total_time()]
        color: str = self.__generate_random_color()
        ram_plot = Plot(name, color, x_values, ram_y_values)
        cpu_plot = Plot(name, color, x_values, cpu_y_values)
        runtime_plot = Plot(name, color, None, runtime)

        # Create header list for current Displayable
        headers: List[Displayable] = list()
        for header in cfile.get_headers():
            headers.append(header.get_name())

        return Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, headers)

    # Generate Random Color for plot
    def __generate_random_color(self):
        random_color: str = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        return random_color

    def setup_connections(self):
        """to be implemented"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
