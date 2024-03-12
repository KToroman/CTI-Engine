import colorsys
from multiprocessing import Queue
from random import random
from typing import List

from PyQt5.QtCore import QRunnable, pyqtSignal

from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.MetricName import MetricName
from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TableWidget import TableWidget


class InsertTableWorker(QRunnable):

    def __init__(self, table: TableWidget, cfile_list: List[CFileReadViewInterface], file_count_signal: pyqtSignal,
                 file_count_queue: Queue, project_time: int):
        super().__init__()

        self.table: TableWidget = table
        self.cfile_list: List[CFileReadViewInterface] = cfile_list
        self.file_count_signal: pyqtSignal = file_count_signal
        self.file_count_queue: Queue = file_count_queue
        self.project_time: int = project_time

    def run(self):
        file_count: int = 0
        print("[TableWorker]   in run")
        for cfile in self.cfile_list:
            print("[TableWorker]   one cfile")
            file_count += 1
            self.table.insert_values(self.__create_displayable(cfile))
        print("[TableWorker]   after insert values")
        self.table.rebuild_table(self.table.rows)
        print("[TableWorker]   after rebuild table")
        self.file_count_queue.put(file_count)
        self.file_count_signal.emit()

    def __create_displayable(self, cfile: CFileReadViewInterface) -> Displayable:
        """Turns given cfile into displayable."""

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
        print("got to here")
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