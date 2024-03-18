from typing import List

from src.view.gui.graph.Plot import Plot
from src.view.gui.graph.Plot import Plot


class Displayable:

    def __init__(self, name: str, ram_plot: Plot, cpu_plot: Plot, runtime_plot: Plot, ram_peak: float, cpu_peak: float, headers: List[str], secondary_headers: List[List[str]]):

        self.name = name
        self.ram_plot = ram_plot
        self.cpu_plot = cpu_plot
        self.runtime_plot = runtime_plot
        self.ram_peak = ram_peak
        self.cpu_peak = cpu_peak
        self.headers = headers
        self.secondary_headers = secondary_headers

        self.name: str = name
        self.ram_plot: Plot = ram_plot
        self.cpu_plot: Plot = cpu_plot
        self.runtime_plot: Plot = runtime_plot
        self.ram_peak: float = ram_peak
        self.cpu_peak: float = cpu_peak
        self.headers: List[str] = headers
        self.secondary_headers: List[List[str]] = secondary_headers
