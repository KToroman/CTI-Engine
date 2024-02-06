from typing import List

from src.view.GUI.Graph import Plot


class Displayable:

    name: str
    ram_plot: Plot
    cpu_plot: Plot
    runtime_plot: Plot
    ram_peak: float
    cpu_peak: float
    headers: List[str] = list()
    secondary_headers: List[List[str]] = list()

    def __init__(self, name: str, ram_plot: Plot, cpu_plot: Plot, runtime_plot: Plot, ram_peak: float, cpu_peak: float, headers: List[str], secondary_headers: List[List[str]]):

        self.name = name
        self.ram_plot = ram_plot
        self.cpu_plot = cpu_plot
        self.runtime_plot = runtime_plot
        self.ram_peak = ram_peak
        self.cpu_peak = cpu_peak
        self.headers = headers
        self.secondary_headers = secondary_headers